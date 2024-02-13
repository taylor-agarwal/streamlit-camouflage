import pytest
import os
import pathlib
from io import BytesIO

DIRECTORY_PATH = pathlib.Path(os.path.dirname(__file__))

@pytest.fixture
def shirt_plaid_red_black_grey() -> BytesIO:
    path = DIRECTORY_PATH / "test_images" / "shirt_plaid_red_black_grey.jpg"
    read_file = open(path, 'rb').read()
    result = BytesIO(read_file)
    return result

@pytest.fixture
def shirt_plaid_red_black_grey_no_background() -> BytesIO:
    path = DIRECTORY_PATH / "test_images" / "shirt_plaid_red_black_grey_no_background.jpg"
    read_file = open(path, 'rb').read()
    result = BytesIO(read_file)
    return result

@pytest.fixture
def shirt_plaid_red_black_grey_colors():
    return {
        (123.98, 32.38, 46.37): 0.44,
        (31.97, 15.66, 24.17): 0.3,
        (207.87, 42.57, 62.11): 0.23,
        (250.66, 248.17, 248.13): 0.04
    }

@pytest.fixture
def shirt_plaid_red_black_grey_color_names():
    return ['brown', 'black', 'crimson', 'snow']

