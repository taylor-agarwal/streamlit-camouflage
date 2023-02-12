import logging

import numpy as np
import streamlit as st

from camouflage.image_utils import extract_clothes
from camouflage.image_color_utils import colors
from camouflage.color_match_utils import check_match

logger = logging.getLogger(__name__)
logging.basicConfig(
    level='info',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

st.markdown("**How to use this app**")

st.markdown("""
    This app will tell you if a set of clothes form a matching outfit.
    First, take pictures of the clothing items in the outfit individually against a neutral background.
    You can take pictures of any clothing item, including shirts, pants, shoes, skirts, hats, ties, scarves, etc.
    The app will attempt to trim down the image to crop as close to the clothing item as possible.
    If the image was cropped incorrectly, you can choose to use the original instead.
    The app will then extract the five primary colors from each image.
    Based on the most frequent color in each item, the app will classify the outfit as 'Basic', 'Neutral', 
    'Analogus', 'Contrast', 'Summer', and/or 'Winter'.
    If the outfit fits at least one classification then the outfit matches!
""")

st.header("Start by picking the how many clothing items you are trying to match")
num_images = st.selectbox("Number of Clothing Items", [0, 1, 2, 3, 4])

if int(num_images) > 0:

    num_images = int(num_images)
    
    images = []
    for i in range(num_images):
        st.subheader(f"Clothing Item {i+1}")
        image = st.camera_input(f"image-{i+1}", label_visibility="hidden")
        images.append(image)

    if not any([image is None for image in images]):
        logger.info("Images collected")
        with st.spinner("Extracting Clothes..."):
            try:
                clothing_images = [extract_clothes(image) for image in images]
            except Exception as e:
                logger.exception(f"Error - Extraction")
                logger.info(str(e))
                st.error("Unable to extract clothes. Please try again.")
                st.stop()
            
            chosen_clothing_images = []
            for i, image_pair in enumerate(clothing_images):
                st.subheader(f"From Item {i+1}")

                if "cropped" in image_pair:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.image(np.array(image_pair["cropped"]), caption="Cropped")
                    with col2:
                        st.image(np.array(image_pair["original"]), caption="Original")

                    choice = st.radio(f"choice_{i}", options=["Cropped", "Original"], horizontal=True, label_visibility="hidden")
                else:
                    st.image(np.array(image_pair["original"]), caption="Original")
                    st.warning("Unable to crop image. Continuing using original image...")

                chosen_clothing_images.append(image_pair[choice.lower()])

        with st.spinner("Extracting Colors..."):
            try:
                clothing_colors = [colors(image) for image in chosen_clothing_images]
            except Exception as e:
                logger.exception(f"Error - Colors")
                logger.info(str(e))
                st.error("Unable to extract colors. Please try again.")
                st.stop()

            st.header("Extracted colors")

            for i, color_pair in enumerate(clothing_colors):
                _, rect_colors = color_pair
                st.subheader(f"Colors From Item {i+1}")
                st.image(rect_colors)


        with st.spinner("Checking for a match..."):
            try:
                outfit_colors = (colors for colors, _ in clothing_colors)
                matches = check_match(outfit_colors)
            except Exception as e:
                logger.exception(f"Error - Match")
                logger.info(str(e))
                st.error("Unable to check a match. Please try again.")
                st.stop()
            
            st.header("This outfit is...")
            for match in matches:
                st.subheader(match)
                st.markdown(outfit_descriptions[match])

            if len(matches) > 0:
                st.header("It's a match!")
            else:
                st.header("It's not a match :(")