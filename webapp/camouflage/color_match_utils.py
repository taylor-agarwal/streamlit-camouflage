from typing import Tuple, Dict
from colorsys import rgb_to_hsv
from camouflage.fuzzy_classifier import GetColorDesc, GetValidMatches


def check_match(outfit_colors):
    """
    Check if two sets of colors match
    """

    primary_rgbs = [tuple(rgb[0][1]) for rgb in outfit_colors]
    primary_rgb_norms = [(r/255.0, g/255.0, b/255.0) for r, g, b in primary_rgbs]
    primary_hsv_norms = [rgb_to_hsv(r, g, b) for r, g, b in primary_rgb_norms]
    primary_hsvs = [(h*360.0, s*100.0, v*100.0) for h, s, v in primary_hsv_norms]

    outfit = [GetColorDesc(hsv) for hsv in primary_hsvs]

    matches = GetValidMatches(outfit)

    return matches
