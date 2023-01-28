import streamlit as st
from camouflage.image_utils import extract_clothes
from camouflage.image_color_utils import colors
from camouflage.color_match_utils import check_match, names
import logging
from streamlit_image_select import image_select
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(
    level='info',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

col1, col2 = st.columns([1, 6])
with col1:
    st.image("images/logo.png")
with col2:
    st.markdown("# Welcome to Camouflage!")

st.write(names)

st.markdown("## Clothing Item 1")
image_1 = st.camera_input("image-1", label_visibility="hidden")

st.markdown("## Clothing Item 2")
image_2 = st.camera_input("image-2", label_visibility="hidden")

if image_1 and image_2:
    logger.info("Images collected")
    with st.spinner("Extracting Clothes..."):
        try:
            clothing_images_1 = extract_clothes(image_1)
            clothing_images_2 = extract_clothes(image_2)
        except Exception as e:
            logger.info(f"Error - Extraction - {e}")
            st.error("Unable to extract clothes. Please try again.")
            st.stop()
        clothing_image_1 = image_select("Choose Image 1", [np.array(img) for img in clothing_images_1], use_container_width=False)
        clothing_image_2 = image_select("Choose Image 2", [np.array(img) for img in clothing_images_2], use_container_width=False)
        
    with st.spinner("Extracting Colors..."):
        try:
            colors_1, rect_colors_1 = colors(clothing_image_1)
            colors_2, rect_colors_2 = colors(clothing_image_2)
        except Exception as e:
            logger.info(f"Error - Colors - {e}")
            st.error("Unable to extract colors. Please try again.")
            st.stop()

        st.markdown("## Image 1")
        st.image(rect_colors_1)

        st.markdown("## Image 2")
        st.image(rect_colors_2)

    with st.spinner("Checking for a match..."):
        try:
            is_match = check_match(colors_1, colors_2)
        except Exception as e:
            logger.info(f"Error - Match - {e}")
            st.error("Unable to check a match. Please try again.")
            st.stop()
        
        if is_match:
            st.markdown("It's a match!")
        else:
            st.markdown("It's not a match :(")