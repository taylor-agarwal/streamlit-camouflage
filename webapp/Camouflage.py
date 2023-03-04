import logging
import traceback
from hashlib import sha256

import numpy as np
import streamlit as st

from camouflage.image_utils import extract_clothes
from camouflage.image_color_utils import colors
from camouflage.color_match_utils import check_match

outfit_descriptions = {
    "Basic": """
- No more than one bright color
- No high contrast between colors (bright warm + dark cool)
- Any number of neutral colors
""",
    "Neutral": """
- Only neutral colors
""",
    "Analogous": """
- All colors must be within the same temp.
- Any number of neutral colors
""",
    "Contrast": """
- At least one warm color
- Both dark and bright colors present
""",
    "Summer": """
- At least two warm colors
- At least one bright color
- At most one dark color
""",
    "Winter": """
- At least one dark color
- No bright colors
"""
}

logger = logging.getLogger(__name__)
logging.basicConfig(
    level='info',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if 'session_num' not in st.session_state:
    id = np.random.randint(1, 999999999)
    st.session_state['session_num'] = id

def user_activity(message):
    logger.info(f"{st.session_state['session_num']} - USER - {message}")

def system_activity(message):
    logger.info(f"{st.session_state['session_num']} - SYSTEM - {message}")

def system_warning(message):
    logger.warning(f"{st.session_state['session_num']} - SYSTEM - {message}")

def system_error(message, e):
    logger.error(f"{st.session_state['session_num']} - SYSTEM - {message}")
    logger.exception(e)

system_activity(f"START")

hide_footer_style = """
    <style>
    footer {visibility: hidden;} 
    #MainMenu {visibility: hidden;} 
    </style>  
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

_, col, _ = st.columns(3)

with col:
    st.image("images/logo.png")

st.title("Welcome to Camouflage!")

st.header("How to Use Camouflage")

st.markdown("""
    Camouflage tells you if the colors in your clothes form a matching outfit.
    First, take pictures of the clothing items in the outfit individually against a neutral background.
    You can take pictures of any clothing item, including shirts, pants, shoes, skirts, hats, ties, scarves, etc.
    Then, it will attempt to trim down the image to crop as close to the clothing item as possible.
    If the image was cropped incorrectly, you can choose to use the original instead.
    Then it will extract the five primary colors from each image.
    Based on the most frequent color in each item, the app will classify the outfit as 'Basic', 'Neutral', 
    'Analogus', 'Contrast', 'Summer', and/or 'Winter'.
    If the outfit fits at least one classification then the outfit matches!
    Use your own judgement when it comes to things like stripes with plaid, or wearing all the same color.
""")

st.header("Start by picking the how many clothing items you are trying to match")
num_images = st.selectbox("Number of Clothing Items", [0, 1, 2, 3, 4], on_change=user_activity, args=("NUMBER INPUT - Number of items changed",))

images = [None]
if int(num_images) > 0:
    system_activity(f"NUMBER INPUT - {num_images} items selected")
    num_images = int(num_images)
    images = []
    for i in range(num_images):
        st.subheader(f"Clothing Item {i+1}")
        image = st.camera_input(f"image-{i+1}", label_visibility="hidden", on_change=user_activity, args=(f"IMAGE CAPTURE - {i+1} - Image changed",))
        images.append(image)

images_taken = not any([image is None for image in images])

clothing_images = []
if images_taken:
    system_activity("CLOTHING EXTRACTION - All images collected, beginning clothing extraction")
    with st.spinner("Extracting Clothes..."):
        for i, image in enumerate(images):
            try:
                clothing_images.append(extract_clothes(image))
                system_activity(f"CLOTHING EXTRACTION - {i+1} - Extracted clothes from image")
            except Exception as e:
                system_error(f"CLOTHING EXTRACTION - {i+1} - Error extracting clothes from images", e)
                st.error("Unable to extract clothes. Please try again.")
                st.stop()

    for i, image_pair in enumerate(clothing_images):
        st.subheader(f"From Item {i+1}")

        system_activity("CHOOSE CLOTHING - {i+1} - Displaying clothing")
        col1, col2 = st.columns(2)

        with col1:
            st.image(np.array(image_pair["cropped"]), caption="Cropped")
        with col2:
            st.image(np.array(image_pair["original"]), caption="Original")

clothing_colors = []
if len(clothing_images) > 0:
    with st.spinner("Extracting Colors..."):
        for i, image in enumerate(clothing_images):
            try:
                clothing_colors.append(colors(image["cropped"]))
                system_activity(f"EXTRACT COLORS - {i+1} - Extracted colors")
            except Exception as e:
                system_error(f"EXTRACT COLORS - {i+1} - Failed to extract colors", e)
                st.error("Unable to extract colors. Please try again.")
                st.stop()

        st.header("Extracted colors")

        for i, color_pair in enumerate(clothing_colors):
            system_activity(f"EXTRACT COLORS - {i+1} - Display colors")
            _, rect_colors = color_pair
            st.subheader(f"Colors From Item {i+1}")
            st.image(rect_colors)

if len(clothing_colors) > 0:
    with st.spinner("Checking for a match..."):
        try:
            outfit_colors = (colors for colors, _ in clothing_colors)
            matches = check_match(outfit_colors)
            system_activity(f"MATCHING - Matches found - {matches}")
        except Exception as e:
            system_error(f"MATCHING - Failed to find outfit matching types", e)
            st.error("Unable to check a match. Please try again.")
            st.stop()
        
        st.header("This outfit is...")
        for match in matches:
            st.subheader(match)
            st.markdown(outfit_descriptions[match])

        if len(matches) > 0:
            st.header("It's a match!")
            system_activity("RESULT - Match")
        else:
            st.header("It's not a match :(")
            system_activity("RESULT - No Match")

system_activity("END")