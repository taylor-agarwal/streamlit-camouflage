from typing import Dict, List, Tuple, NewType

import streamlit as st

from io import BytesIO
from PIL import Image
from rembg import remove, new_session

import numpy as np
from sklearn.cluster import KMeans
from colorsys import rgb_to_hsv

from camouflage.fuzzy_classifier import GetValidMatches, GetColorDesc

@st.cache_resource
def get_session():
    return new_session("u2netp")

SESSION = get_session()

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
        for pct, color in zip(color_hist, colors):
            color = tuple(color.tolist())
            image_colors[color] = pct

        self.colors = image_colors

    def get_colors(self):
        pct_colors = sorted([(percent, color) for color, percent in self.colors.items()])
        colors = [color for _, color in pct_colors]
        return colors

    def get_color_rect(self, height: int = 50, width: int = 300) -> np.ndarray:
        if not self.colors:
            self.extract_colors()

        color_rect = []
        img_colors = sorted([(percent, color) for color, percent in self.colors.items()])
        for percent, color in img_colors:
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
