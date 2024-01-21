import logging
import sys
from typing import List

import numpy as np
import streamlit as st
from PIL import Image

sys.path.insert(0, ".")

from webapp.utils.constants import HIDE_FOOTER_STYLE, TITLE_HTML, CLOTHING_NUMBER_CHOICES, OUTFIT_DESCRIPTIONS, COLUMN_STYLE, STATEMENT_OUTFITS
from webapp.utils.webutils import get_color_rect, api_request

# TODO: Make it so if all pixels are black, it returns the whole black image
# TODO: Improve the theme (white and light green/tan?)

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Track sessions
if 'session_num' not in st.session_state:
    id = np.random.randint(1, 999999999)
    st.session_state['session_num'] = id

# Logging message types
def user_activity(message):
    logger.info(f"{st.session_state['session_num']} - USER - {message}")

def system_activity(message):
    logger.info(f"{st.session_state['session_num']} - SYSTEM - {message}")

def system_warning(message):
    logger.warning(f"{st.session_state['session_num']} - SYSTEM - {message}")

def system_error(message, e):
    logger.error(f"{st.session_state['session_num']} - SYSTEM - {message}")
    logger.exception(e)

system_activity("START")

# Hide streamlit header and footer
st.markdown(HIDE_FOOTER_STYLE, unsafe_allow_html=True)

st.write(COLUMN_STYLE, unsafe_allow_html=True)

st.markdown("#")

st.write(TITLE_HTML, unsafe_allow_html=True)

st.markdown("##")

help_clicked = st.button(label="How do I use this app?", use_container_width=True)
if help_clicked:
    st.switch_page("pages/About.py")

# User select number of images
num_images = st.selectbox("Number of Clothing Items", CLOTHING_NUMBER_CHOICES, on_change=user_activity, args=("NUMBER INPUT - Number of items changed",))
system_activity(f"NUMBER INPUT - {num_images} items selected")

tabs = None
if int(num_images) > 0:
    tabs = st.tabs([f"Item {i+1}" for i in range(num_images)])

chosen_colors = []
for i, tab in enumerate(tabs):
    with tab:
        # Generate camera input dialogues
        image = st.camera_input(f"image-{i+1}", label_visibility="hidden", on_change=user_activity, args=(f"IMAGE CAPTURE - {i+1} - Image changed",))
        image_rembg_bytes = None
        if image is not None:
            # Remove background from image
            files = {"file": image}
            route = "rembg"
            response = api_request(route=route, files=files)
            image_rembg_bytes = response.content
            # im = io.BytesIO(response.content)
            # image_rembg = PILImage.open(im).convert('RGB')
            # st.image(image_rembg)
        if image_rembg_bytes is not None:
            # Extract and display colors
            files = {'file': image_rembg_bytes}
            route = "colors"
            response = api_request(route=route, files=files)
            colors_json = response.json()
            system_activity(f"COLOR EXTRACTION - {i+1} - Colors {colors_json}")
            colors = colors_json['colors']
            columns = st.columns(4)
            for j, column in enumerate(columns):
                with column:
                    color = colors[j]
                    hex = color['hex']
                    # name = color['name']
                    st.color_picker(label=hex, value=hex, key=f"color_picker_{i}_{j}", label_visibility='hidden')
                    default = True if j == 0 else False
                    picked = st.checkbox(label=f"color_choice_{i}_{j}", value=default, label_visibility="hidden")
                    if picked:
                        chosen_colors.append(color)

if len(chosen_colors) > 0:
    width = 500
    height = 100
    for c in chosen_colors:
        c['pct'] = 1 / len(chosen_colors)
    rect = get_color_rect(colors=chosen_colors, width=width, height=height)
    with st.container(border=True):
        st.image(rect, use_column_width=True)

submitted = st.button("Check My Outfit!", use_container_width=True)

# Display the colors from the items
# https://blog.streamlit.io/create-a-color-palette-from-any-image/ 

if submitted:
    with st.spinner("Checking..."):
        st.divider()
        # Determine if the colors are a match
        matches = None
        if len(chosen_colors) > 0:
            # Check outfit for matches
            with st.spinner("Checking for a match..."):
                try:
                    json = {"colors": chosen_colors}
                    route = "matches"
                    response = api_request(route=route, json=json)
                    matches = response.json()
                    matches = matches['matches']
                    system_activity(f"MATCHING - Matches found - {matches}")
                except Exception as e:
                    system_error(f"MATCHING - Failed to find outfit matching types", e)
                    st.error("Unable to check a match. Please try again.")
                    st.stop()
                
                if len(matches) > 0:
                    st.header("It's a match!")
                    if all([match in STATEMENT_OUTFITS for match in matches]):
                        st.write("""Note: This outfit may be considered a "statement", so wear it only if you're sure about it.""")
                    system_activity("RESULT - Match")
                else:
                    st.header("It's not a match :(")
                    system_activity("RESULT - No Match")

                st.subheader("This outfit is...")
                for match in matches:
                    st.text(match, help=OUTFIT_DESCRIPTIONS[match])


        else:
            st.warning("No colors selected - Please take your image(s) and select some colors before continuing")

st.markdown('##')
# Show feedback link
with st.container():
    st.link_button(":gift: Give Feedback!", "https://forms.gle/PTqChvC2sJUB5B6NA", use_container_width=True)

system_activity("END")