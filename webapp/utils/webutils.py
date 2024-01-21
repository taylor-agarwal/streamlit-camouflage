import numpy as np
from typing import List

import requests
import streamlit as st

from webapp.utils.constants import API_ROUTES


def get_color_rect(colors: List[dict], height: int = 50, width: int = 300) -> np.ndarray:
    """Get a numpy array of shape (width, height, 3) containing proportional amounts of each color in the
    clothing image

    Args:
        height (int, optional): Height of the color rectangle in pixels. Defaults to 50.
        width (int, optional): Width of the color rectangle in pixels. Defaults to 300.

    Returns:
        np.ndarray: _description_
    """

    color_rect = []
    for color in colors:
        _color = [color['r'], color['g'], color['b']]
        _color = [c / 255.0 for c in _color]

        if len(colors) == 1:
            color_width = width
        else:
            percent = color['pct']
            color_width = int(percent * width)

        rect_color = np.zeros([height, color_width, 3])
        rect_color = np.full_like(rect_color, _color)
        color_rect.append(rect_color)
    return np.concatenate(color_rect, axis=1)

@st.cache_resource(show_spinner=False)
def api_request(route: str, files: dict = None, json: dict = None):
    response = requests.post(API_ROUTES[route], files=files, json=json, stream=True)
    response.raise_for_status()
    return response