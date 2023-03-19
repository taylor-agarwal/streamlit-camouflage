import logging
import tracemalloc

import numpy as np
import streamlit as st

from camouflage.objects import Clothing, Outfit

# TODO: Make it so if all pixels are black, it returns the whole black image

tracemalloc.start()
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

system_activity("START")

hide_footer_style = """
    <style>
    footer {visibility: hidden;} 
    #MainMenu {visibility: hidden;} 
    </style>  
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')
with col2:
    st.image("images/logo.png")
with col3:
    st.write(' ')

title = """
<center>
<h1>Welcome to Camouflage!</h1>
<h5><em>Helping the Colorblind Blend In</em></h5>
</center>
"""

st.write(title, unsafe_allow_html=True)

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

outfit = None
clothes = []
if images_taken:
    system_activity("CLOTHING EXTRACTION - All images collected, beginning clothing extraction")
    with st.spinner("Extracting Clothes..."):
        for i, image in enumerate(images):
            try:
                clothing = Clothing(image)
                clothing.rembg()
                clothes.append(clothing)
                system_activity(f"CLOTHING EXTRACTION - {i+1} - Extracted clothes from image")
            except Exception as e:
                system_error(f"CLOTHING EXTRACTION - {i+1} - Error extracting clothes from images", e)
                st.error("Unable to extract clothes. Please try again.")
                st.stop()

    outfit = Outfit(clothes=clothes)
    for i, clothing in enumerate(outfit):
        system_activity("CLOTHING EXTRACTION - {i+1} - Displaying clothing")
        st.subheader(f"From Item {i+1}")
        st.image(clothing.image_rembg, caption="Cropped")

if outfit:
    with st.spinner("Extracting Colors..."):
        for i, clothing in enumerate(outfit):
            try:
                clothing.extract_colors()
                system_activity(f"EXTRACT COLORS - {i+1} - Extracted colors")
            except Exception as e:
                system_error(f"EXTRACT COLORS - {i+1} - Failed to extract colors", e)
                st.error("Unable to extract colors. Please try again.")
                st.stop()

        st.header("Extracted colors")

        for i, clothing in enumerate(outfit):
            system_activity(f"EXTRACT COLORS - {i+1} - Display colors")
            st.subheader(f"Colors From Item {i+1}")
            st.image(clothing.get_color_rect())

if outfit:
    with st.spinner("Checking for a match..."):
        try:
            matches = outfit.get_matches()
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

with st.container():
    st.write("<a href='https://forms.gle/PTqChvC2sJUB5B6NA'>Give Feedback</a>", unsafe_allow_html=True)

system_activity("END")
system_activity(f"Memory allocation (current, peak): {tracemalloc.get_traced_memory()}")
tracemalloc.stop()