from streamlit_camouflage.v1.objects import Image, Clothing
from PIL import Image as PILImage
from io import BytesIO
import pathlib
import os

DIRECTORY_PATH = pathlib.Path(os.path.dirname(__file__))

def test_image(shirt_plaid_red_black_grey, shirt_plaid_red_black_grey_no_background):
    # Create an image object
    image_bytes = shirt_plaid_red_black_grey
    im = Image(image_bytes=image_bytes)

    assert type(im.image_bytes) == BytesIO
    assert type(im.image) == PILImage.Image

    # Remove the background
    im_rembg = im.rembg()

    assert type(im_rembg) == bytes
    assert im_rembg == shirt_plaid_red_black_grey_no_background.read()

def test_clothing(
        shirt_plaid_red_black_grey_no_background, 
        shirt_plaid_red_black_grey_colors,
        shirt_plaid_red_black_grey_color_names
    ):
    # Create a clothing object
    image_bytes = shirt_plaid_red_black_grey_no_background
    clothing = Clothing(image_bytes=image_bytes)
    
    assert type(clothing.image_bytes) == BytesIO
    assert type(clothing.image) == PILImage.Image
    assert clothing.colors is None

    # Extract colors from the object
    n = 4
    clothing.extract_colors(n=n)

    assert type(clothing.colors) == dict
    assert len(clothing.colors) == n

    colors = {tuple([round(f, 2) for f in k]): round(v, 2) for k, v in clothing.colors.items()}

    assert colors == shirt_plaid_red_black_grey_colors

    # Fetch the extracted colors
    fetched_colors = clothing.get_colors()
    fetched_colors = [tuple([round(f, 2) for f in color]) for color in fetched_colors]
    expected_colors = [tuple([round(f, 2) for f in k]) for k, _ in shirt_plaid_red_black_grey_colors.items()]
    assert fetched_colors == expected_colors

    # Get the names of the colors
    fetched_color_names = clothing.get_color_names()
    expected_color_names = shirt_plaid_red_black_grey_color_names
    assert fetched_color_names == expected_color_names