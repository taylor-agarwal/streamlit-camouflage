from io import BytesIO
from typing import Dict, List, Tuple, NewType

from colorsys import rgb_to_hsv
import numpy as np
from PIL import Image
from rembg import remove, new_session
from scipy.spatial import KDTree
from sklearn.cluster import KMeans
import streamlit as st
from webcolors import (
    CSS3_HEX_TO_NAMES,
    hex_to_rgb,
)

from streamlit_camouflage.v1.fuzzy_classifier import GetValidMatches, GetColorDesc

@st.cache_resource
def get_session():
    return new_session("u2netp")

@st.cache_resource
def get_kdt_db():
    names = []
    rgb_values = []
    for color_hex, color_name in CSS3_HEX_TO_NAMES.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))
    
    return names, KDTree(rgb_values)

SESSION = get_session()

COLOR_NAMES, KDT_DB = get_kdt_db()

Colors = NewType('Colors', Dict[Tuple[float, float, float], float])

DEFAULT_EXTRACT_N = 4
DENOISE_N = 2

class Clothing:
    """Describes an article of clothing"""

    def __init__(self, image_bytes: BytesIO):
        """
        Args:
            image_bytes (BytesIO): Image of the clothing item
        """
        self.image_bytes: BytesIO = image_bytes
        self.image: np.ndarray = Image.open(image_bytes).convert('RGB')
        self.image_rembg: np.ndarray = None
        self.colors: Colors = None
        self.n_colors: int = None

    def rembg(self):
        """Remove background from the clothing image"""
        self.image_rembg = remove(self.image, session=SESSION).convert('RGB')

    def set_n_colors(self, n: int):
        """Set the maximum number of colors in the clothing item

        Args:
            n (int): The maximum number of colors
        """
        self.n_colors = n
        if self.colors is not None:
            self.extract_colors()

    def extract_colors(self):
        """Extract the colors from clothing image

        Args:
            n (float, optional): Number of colors to extract from the image. Defaults to 4.
        """
        if not self.image_rembg:
            self.rembg()
        
        pixels = np.array([pixel for row in np.array(self.image_rembg) for pixel in row if sum(pixel) != 0])
    
        # Find clusters of colors to determine dominant colors
        n = self.n_colors + DENOISE_N if self.n_colors is not None else DEFAULT_EXTRACT_N
        color_cluster = KMeans(n_clusters=n, random_state=1).fit(pixels)
        cluster, colors = color_cluster, color_cluster.cluster_centers_
        
        # Compute the percent of the pixels containing that color
        color_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
        (color_hist, _) = np.histogram(cluster.labels_, bins = color_labels)
        color_hist = color_hist.astype("float")
        color_hist /= color_hist.sum()

        # Remove the noise colors
        image_colors = dict()
        pct_colors = sorted([(percent, color) for percent, color in zip(color_hist, colors)])[::-1]
        pct_colors = pct_colors[:(-1*DENOISE_N)]
        total_pct = sum([percent for percent, color in pct_colors])
        pct_colors = [(percent / total_pct, color) for percent, color in pct_colors]

        # Save the color and the percent of pixels with that color
        for pct, color in pct_colors:
            color = tuple(color.tolist())
            image_colors[color] = pct

        self.colors = image_colors


    def get_colors(self) -> List[Tuple[float, float, float]]:
        """Gets the list of colors as rgb values in order of frequency

        Args:
            lim (int, optional): Limit the number of colors to return. If lim is None, all extracted colors are returned

        Returns:
            List[Tuple[float, float, float]]: Ordered rgb tuples ordered based on frequency in the image
        """
        colors = [color for color, _ in self.colors.items()]
        return colors

    def get_color_names(self) -> List[str]:
        """Gets the names of the colors as strings in order of frequency

        Args:
            lim (int, optional): Maximum number of colors to name in each output. If None, all extracted colors are outputted

        Returns:
            List[str]: List of color names in order of frequency in the clothing image
        """
        color_names = []
        for color in self.get_colors():
            distance, index = KDT_DB.query(color)
            color_names.append(COLOR_NAMES[index])
        return color_names

    def get_color_rect(self, height: int = 50, width: int = 300) -> np.ndarray:
        """Get a numpy array of shape (width, height, 3) containing proportional amounts of each color in the
        clothing image

        Args:
            height (int, optional): Height of the color rectangle in pixels. Defaults to 50.
            width (int, optional): Width of the color rectangle in pixels. Defaults to 300.

        Returns:
            np.ndarray: _description_
        """
        if not self.colors:
            self.extract_colors()

        color_rect = []
        for color, percent in self.colors.items():
            color = [c / 255.0 for c in color]
            color_width = int(percent * width)
            rect_color = np.zeros([height, color_width, 3])
            rect_color = np.full_like(rect_color, color)
            color_rect.append(rect_color)
        return np.concatenate(color_rect, axis=1)

class Outfit:
    """Describes a collection of clothing in an outfit"""

    def __init__(self, clothes: List[Clothing]):
        """
        Args:
            clothes (List[Clothing]): List of clothing items in the outfit
        """
        self.clothes: List[Clothing] = clothes

    def __iter__(self):
        return iter(self.clothes)

    def get_matches(self) -> List[str]:
        """Get names of outfit match types

        Returns:
            List[str]: List of names of outfit match types
        """
        rgbs = sum([clothing.get_colors() for clothing in self], start=[])
        rgb_norms = [(r/255.0, g/255.0, b/255.0) for r, g, b in rgbs]
        hsv_norms = [rgb_to_hsv(r, g, b) for r, g, b in rgb_norms]
        hsvs = [(h*360.0, s*100.0, v*100.0) for h, s, v in hsv_norms]

        outfit = [GetColorDesc(hsv) for hsv in hsvs]

        matches = GetValidMatches(outfit)

        return matches
