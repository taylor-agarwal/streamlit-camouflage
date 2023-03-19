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

from camouflage.fuzzy_classifier import GetValidMatches, GetColorDesc

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

class Clothing:

    def __init__(self, image_bytes: BytesIO):
        self.image_bytes: BytesIO = image_bytes
        self.image: np.ndarray = Image.open(image_bytes).convert('RGB')
        self.image_rembg: np.ndarray = None
        self.colors: Colors = None

    def rembg(self):
        self.image_rembg = remove(self.image, session=SESSION).convert('RGB')

    def extract_colors(self, n: float = 4):
        if not self.image_rembg:
            self.rembg()
        
        pixels = np.array([pixel for row in np.array(self.image_rembg) for pixel in row if sum(pixel) != 0])
    
        # Find clusters of colors to determine dominant colors
        color_cluster = KMeans(n_clusters=n, random_state=1).fit(pixels)
        cluster, colors = color_cluster, color_cluster.cluster_centers_
        
        # Compute the percent of the pixels containing that color
        color_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
        (color_hist, _) = np.histogram(cluster.labels_, bins = color_labels)
        color_hist = color_hist.astype("float")
        color_hist /= color_hist.sum()

        # Save the color and the percent of pixels with that color
        image_colors = dict()
        pct_colors = sorted([(percent, color) for percent, color in zip(color_hist, colors)])
        for pct, color in pct_colors:
            color = tuple(color.tolist())
            image_colors[color] = pct

        self.colors = image_colors

    def get_colors(self) -> List[Tuple[float, float, float]]:
        colors = [color for color, _ in self.colors.items()]
        return colors

    def get_color_names(self):
        color_names = []
        for color in self.get_colors():
            distance, index = KDT_DB.query(color)
            color_names.append(COLOR_NAMES[index])
        return color_names

    def get_color_rect(self, height: int = 50, width: int = 300) -> np.ndarray:
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

    def __init__(self, clothes: List[Clothing]):
        self.clothes: List[Clothing] = clothes

    def __iter__(self):
        return iter(self.clothes)

    def get_matches(self):
        primary_rgbs = [clothing.get_colors()[0] for clothing in self]
        primary_rgb_norms = [(r/255.0, g/255.0, b/255.0) for r, g, b in primary_rgbs]
        primary_hsv_norms = [rgb_to_hsv(r, g, b) for r, g, b in primary_rgb_norms]
        primary_hsvs = [(h*360.0, s*100.0, v*100.0) for h, s, v in primary_hsv_norms]

        outfit = [GetColorDesc(hsv) for hsv in primary_hsvs]

        matches = GetValidMatches(outfit)

        return matches
