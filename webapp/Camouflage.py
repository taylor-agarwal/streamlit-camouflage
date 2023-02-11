import streamlit as st
from camouflage.image_utils import extract_clothes
from camouflage.image_color_utils import colors
from camouflage.color_match_utils import check_match
import logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(
    level='info',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    First take pictures of the individual clothing items you want to wear against a neutral background.
    The app will attempt to trim down the image to crop as close to the clothing item as possible.
    If the image was cropped incorrectly, you can choose to use the original instead.
    The app will then extract the five primary colors from each image.
    Based on the two most frequent colors, the app will classify the outfit as 'Basic', 'Neutral', 'Analogus', 'Contrast', 'Summer', 'Winter'.
    See the **About** section for more information about what each classification means.
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
            st.markdown(", ".join(matches))

            if len(matches) > 0:
                st.header("It's a match!")
            else:
                st.header("It's not a match :(")