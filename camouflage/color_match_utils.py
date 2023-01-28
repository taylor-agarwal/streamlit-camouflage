from typing import Tuple, Dict
from colorsys import rgb_to_hsv
from camouflage.fuzzy_classifier import GetColorDesc, GetValidMatches


def check_match(colors_1, colors_2):
    """
    Check if two sets of colors match
    """

    primary_hsv_1 = rgb_to_hsv(*colors_1[0][1])
    primary_hsv_2 = rgb_to_hsv(*colors_2[0][1])

    desc_1 = GetColorDesc(primary_hsv_1)
    desc_2 = GetColorDesc(primary_hsv_2)

    outfit = (desc_1, desc_2)

    matches = GetValidMatches(outfit)

    return matches
