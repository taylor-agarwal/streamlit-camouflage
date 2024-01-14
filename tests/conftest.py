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
        (124.03, 32.38, 46.37): 0.44, 
        (31.99, 15.66, 24.17): 0.3, 
        (207.93, 42.6, 62.15): 0.23, 
        (250.67, 248.17, 248.14): 0.04
    }

@pytest.fixture
def shirt_plaid_red_black_grey_color_names():
    return ['brown', 'black', 'crimson', 'snow']

