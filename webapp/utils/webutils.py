import numpy as np
from typing import List


def rgb_to_hex(rgb):
    _rgb = tuple([int(c) for c in rgb])
    print(_rgb)
    hex = '#%02x%02x%02x' % _rgb
    return hex


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

        percent = color['pct']
        color_width = int(percent * width)

        rect_color = np.zeros([height, color_width, 3])
        rect_color = np.full_like(rect_color, _color)
        color_rect.append(rect_color)
    return np.concatenate(color_rect, axis=1)