import logging
import tracemalloc

import numpy as np
import streamlit as st
import requests
from PIL import Image as PILImage
import io

from webapp.utils.webutils import get_color_rect

# TODO: Make it so if all pixels are black, it returns the whole black image

# Start memory tracing
tracemalloc.start()

# Declare API endpoints
API_ENDPOINT = "http://localhost:80/v1"
API_ROUTES = {
    "colors": API_ENDPOINT + "/colors",
    "matches": API_ENDPOINT + "/matches",
    "rembg": API_ENDPOINT + "/rembg"
}

# Write outfit descriptions
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
hide_footer_style = """
    <style>
    footer {visibility: hidden;} 
    #MainMenu {visibility: hidden;} 
    </style>  
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

# Create title
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
<text>If you do not see the logo above, please refresh the page</text>
</center>
"""

st.write(title, unsafe_allow_html=True)

# User select number of images
num_images = st.selectbox("Number of Clothing Items", [0, 1, 2, 3, 4], on_change=user_activity, args=("NUMBER INPUT - Number of items changed",))

# Generate camera input dialogues
images = [None]
if int(num_images) > 0:
    system_activity(f"NUMBER INPUT - {num_images} items selected")
    num_images = int(num_images)
    images = []
    for i in range(num_images):
        image = st.camera_input(f"image-{i+1}", label_visibility="hidden", on_change=user_activity, args=(f"IMAGE CAPTURE - {i+1} - Image changed",))
        images.append(image)

# If all the images have been taken, start processing them and put them in an outfit
images_taken = not any([image is None for image in images])
images_rembg = []
if images_taken:
    st.header("Cropped Images")
    system_activity("CLOTHING EXTRACTION - All images collected, beginning clothing extraction")
    with st.spinner("Extracting Clothes..."):
        # Save clothes and remove backgrounds
        for i, image in enumerate(images):
            try:
                # Remove background from image
                files = {"file": image}
                response = requests.post(API_ROUTES["rembg"], files=files, stream=True)
                response.raise_for_status()
                im = io.BytesIO(response.content)
                image_rembg = PILImage.open(im).convert('RGB')
                images_rembg.append(im)
                st.image(images_rembg, caption=f"From Item {i+1}")
                system_activity(f"CLOTHING EXTRACTION - {i+1} - Extracted clothes from image")
            except Exception as e:
                system_error(f"CLOTHING EXTRACTION - {i+1} - Error extracting clothes from images", e)
                st.error("Unable to extract clothes. Please try again.")
                st.stop()

# Display the colors from the item
outfit = []
if len(images_rembg) > 0:
    st.header("Extracted Colors")
    system_activity("COLOR EXTRACTION - Extracting colors from all images")
    with st.spinner("Extracting Colors..."):
        for i, image in enumerate(images_rembg):
            try:
                files = {'file': image}
                response = requests.post(API_ROUTES["colors"], files=files)
                response.raise_for_status()
                colors = response.json()
                system_activity(f"COLOR EXTRACTION - {i+1} - Colors {colors}")
                outfit.append(colors)
                rect = get_color_rect(colors['colors'])
                st.image(rect, caption=f"Colors From Item {i+1}")
                st.write(f"Colors: {', '.join([color['name'] for color in colors['colors']])}")
            except Exception as e:
                system_error(f"COLOR EXTRACTION - {i+1} - Error extracting colors from images", e)
                st.error("Unable to extract clothes. Please try again.")
                st.stop()


# If the outfit is created, try extracting and displaying the colors from each clothing item
if len(outfit) > 0:
    # Check outfit for matches
    with st.spinner("Checking for a match..."):
        try:
            body = {"outfit": outfit}
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
            st.subheader(match)
            st.markdown(outfit_descriptions[match])

        st.write(f"Results are based on the primary color of each clothing item only.")

        if len(matches) > 0:
            st.header("It's a match!")
            system_activity("RESULT - Match")
        else:
            st.header("It's not a match :(")
            system_activity("RESULT - No Match")

# Show feedback link
if outfit:
    with st.container():
        st.write("<a href='https://forms.gle/PTqChvC2sJUB5B6NA'>Give Feedback</a>", unsafe_allow_html=True)

# Log memory usage
system_activity("END")
system_activity(f"Memory allocation (current, peak): {tracemalloc.get_traced_memory()}")
tracemalloc.stop()