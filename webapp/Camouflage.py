import logging
import sys
from typing import List

import numpy as np
import streamlit as st
import requests
from PIL import Image as PILImage
import io

sys.path.insert(0, ".")

from webapp.utils.constants import HIDE_FOOTER_STYLE, TITLE_HTML, CLOTHING_NUMBER_CHOICES, API_ROUTES, OUTFIT_DESCRIPTIONS, ENVIRONMENT
from webapp.utils.webutils import get_color_rect

# TODO: Make it so if all pixels are black, it returns the whole black image
# TODO: Make each tab a different image, with extracted colors and color picking below them
# TODO: Display the chosen colors side-by-side above the outcome

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
if ENVIRONMENT == "prod":
    st.markdown(HIDE_FOOTER_STYLE, unsafe_allow_html=True)

# Create title
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image("images/logo.png")
with col3:
    st.write(' ')

st.write(TITLE_HTML, unsafe_allow_html=True)

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
            response = requests.post(API_ROUTES["rembg"], files=files, stream=True)
            response.raise_for_status()
            image_rembg_bytes = response.content
            # im = io.BytesIO(response.content)
            # image_rembg = PILImage.open(im).convert('RGB')
            # st.image(image_rembg)
        if image_rembg_bytes is not None:
            # Extract and display colors
            files = {'file': image_rembg_bytes}
            response = requests.post(API_ROUTES["colors"], files=files, stream=True)
            response.raise_for_status()
            colors_json = response.json()
            system_activity(f"COLOR EXTRACTION - {i+1} - Colors {colors_json}")
            colors = colors_json['colors']
            columns = st.columns(len(colors))
            colors_name = [color['name'] for color in colors]
            colors_hex = [color['hex'] for color in colors]
            for j, column in enumerate(columns):
                with column:
                    hex = colors_hex[j]
                    name = colors_name[j]
                    st.color_picker(label=name, value=hex, key=f"color_picker_{i}_{j}")
                    default = True if j == 0 else False
                    picked = st.checkbox(label=f"color_choice_{i}_{j}", value=default, label_visibility="hidden")
                    if picked:
                        chosen_colors.append(colors[j])

submitted = st.button("Check My Outfit!", use_container_width=True)

# TODO: Consider storing colors and only rerunning above lines if the images change - st.session_state colors with callback on images on_change
# Display the colors from the items
# https://blog.streamlit.io/create-a-color-palette-from-any-image/ 

if submitted:
    with st.spinner("Checking..."):
        st.divider()
        # Determine if the colors are a match
        matches = None
        if len(chosen_colors) > 0:
            width = 500
            height = 200
            for c in chosen_colors:
                c['pct'] = 1 / len(chosen_colors)
            rect = get_color_rect(colors=chosen_colors, width=width, height=height)
            _, col, _ = st.columns([1, 4, 1])
            with col:
                with st.container(border=True):
                    st.image(rect, use_column_width=True)
            # Check outfit for matches
            with st.spinner("Checking for a match..."):
                try:
                    body = {"colors": chosen_colors}
                    response = requests.post(API_ROUTES["matches"], json=body)
                    response.raise_for_status()
                    matches = response.json()
                    matches = matches['matches']
                    system_activity(f"MATCHING - Matches found - {matches}")
                except Exception as e:
                    system_error(f"MATCHING - Failed to find outfit matching types", e)
                    st.error("Unable to check a match. Please try again.")
                    st.stop()
                
                st.header("This outfit is...")
                for match in matches:
                    st.subheader(match, help=OUTFIT_DESCRIPTIONS[match])

                if len(matches) > 0:
                    st.header("It's a match!")
                    system_activity("RESULT - Match")
                else:
                    st.header("It's not a match :(")
                    system_activity("RESULT - No Match")

# Show feedback link
with st.container():
    st.write("<a href='https://forms.gle/PTqChvC2sJUB5B6NA'>Give Feedback</a>", unsafe_allow_html=True)

system_activity("END")