import logging
import sys

import numpy as np
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image

sys.path.insert(0, ".")

from webapp.utils.constants import HIDE_FOOTER_STYLE, PAGE_HEADER_HTML, CLOTHING_NUMBER_CHOICES, OUTFIT_DESCRIPTIONS, COLUMN_STYLE, STATEMENT_OUTFITS
from webapp.utils.webutils import get_color_rect, api_request

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

if 'colors' not in st.session_state:
    st.session_state['colors'] = []

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

st.write(PAGE_HEADER_HTML, unsafe_allow_html=True)

st.markdown("##")

# Generate camera input dialogues
st.subheader("1️⃣ Take a picture of your outfit")
uploaded_image = st.camera_input(f"image", label_visibility="hidden", on_change=user_activity, args=(f"IMAGE CAPTURE - Image changed",))
if uploaded_image is not None:
    st.subheader("2️⃣ Touch the image below to pick out colors")
    image = Image.open(uploaded_image)
    image_ndarray = np.array(image)
    coords = streamlit_image_coordinates(image_ndarray)
    if coords:
        color = image_ndarray[coords['y'], coords['x']]
        c = {
            "r": float(color[0]), 
            "g": float(color[1]), 
            "b": float(color[2]), 
            "hex": "",
            "pct": 0.0,
            "name": ""
        }
        if c not in st.session_state['colors']:
            st.session_state['colors'].append(c)

chosen_colors = [c.copy() for c in st.session_state['colors']]
submitted = False
if len(chosen_colors) > 0:
    width = 500
    height = 100
    for c in chosen_colors:
        c['pct'] = 1 / len(chosen_colors)
    rect = get_color_rect(colors=chosen_colors, width=width, height=height)
    with st.container(border=True):
        st.image(rect, use_column_width=True)

    submitted = st.button("3️⃣ Check My Outfit!", use_container_width=True)

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

                for match in matches:
                    with st.container(border=True):
                        st.markdown(f"<center><h3>{match}</h3></center>", unsafe_allow_html=True)
                        st.write(OUTFIT_DESCRIPTIONS[match])


        else:
            st.warning("No colors selected - Please take your image(s) and select some colors before continuing")

st.markdown('##')
# Show feedback link
with st.container():
    st.link_button(":gift: Give Feedback!", "https://forms.gle/PTqChvC2sJUB5B6NA", use_container_width=True)

system_activity("END")