from typing import Tuple, Dict
from colorsys import hls_to_rgb, rgb_to_hls
from webcolors import hex_to_rgb, CSS3_HEX_TO_NAMES
from scipy.spatial import KDTree

TESTING = True

css3_db = CSS3_HEX_TO_NAMES
names = [name for _, name in css3_db.items()]
rgb_values = [hex_to_rgb(color_hex) for color_hex, _ in css3_db.items()]
hls_values = [rgb_to_hls(*(c / 255. for c in color_rgb)) for color_rgb in rgb_values]

kdt_db = KDTree(hls_values)


def transform_colors(rgb: Tuple[float]) -> Dict[str, Tuple[float]]:
    """
    Computes the complementary colors for a given color
    Args:
        rgb (tuple of floats): Tuple of the form (r, g, b) where 0 < r,g,b < 255
    Returns:
        dict of tuples: Dictionary with rgb and hls values for the given color and its complements
    """
    rgb = (x / 255. for x in rgb)
    hls = rgb_to_hls(*rgb)
    h = hls[0]
    if h < 0.5:
        h_c = h + 0.5
    else:
        h_c = h - 0.5
    hls_c = (h_c, hls[1], hls[2])
    rgb_c = hls_to_rgb(*hls_c)
    color_dict = {
        "rgb": rgb,
        "rgb_c": rgb_c,
        "hls": hls,
        "hls_c": hls_c
    }
    return color_dict


def rgb_to_name(rgb: Tuple[float]) -> str:
    """
    Args:
        rgb (tuple of floats): Tuple of the form (r, g, b) where 0 < r,g,b < 255
    """
    hls = transform_colors(rgb)['hls']
    _, index = kdt_db.query(hls)
    return f'{names[index]}'


# TODO: This
def named_match(colors_1, colors_2):

    # Get names of primary colors
    color_names_1 = [rgb_to_name(rgb) for _, rgb in colors_1]
    color_names_2 = [rgb_to_name(rgb) for _, rgb in colors_2]

    names_1 = ["green"]
    names_2 = ["blue"]
    return True


def complement(rgb):
    return transform_colors(rgb)['rgb_c']


# TODO: This
def complement_match(colors_1, colors_2):

    # Compute complements
    complements_1 = [complement(rgb) for _, rgb in colors_1]
    complements_2 = [complement(rgb) for _, rgb in colors_2]

    return 


# TODO: This
def trio(rgb):

    trio_1 = (1, 2, 3)
    trio_2 = (4, 5, 6)
    return (trio_1, trio_2)


# TODO: This
def trio_match(colors_1, colors_2):

    # Compute trios
    trios_1 = [trio(rgb) for _, rgb in colors_1]
    trios_2 = [trio(rgb) for _, rgb in colors_2]



def check_match(colors_1, colors_2):
    """
    Check if two sets of colors match
    """
    if TESTING:
        return True

    # Check if any names match by rule
    is_named_match = named_match(colors_1, colors_2)
    if is_named_match:
        return True

    # Check if any colors match by complement
    is_complement_match = complement_match(colors_1, colors_2)
    if is_complement_match:
        return True

    # Check if any colors match by trio
    is_trio_match = trio_match(colors_1, colors_2)
    if is_trio_match:
        return True

    return False
