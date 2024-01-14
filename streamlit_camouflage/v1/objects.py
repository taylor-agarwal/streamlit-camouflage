import io
from io import BytesIO
from typing import Dict, List, Tuple, NewType
import logging

import numpy as np
from PIL import Image as PILImage
from rembg import remove, new_session
from scipy.spatial import KDTree
from sklearn.cluster import KMeans
from webcolors import (
    CSS3_HEX_TO_NAMES,
    hex_to_rgb,
)

def get_session():
    return new_session("u2netp")

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

logger = logging.getLogger()


class Image:
    """Describes an image."""

    def __init__(self, image_bytes: BytesIO):
        """
        Args:
            image_bytes (BytesIO): Image of the clothing item
        """
        self.image_bytes: BytesIO = image_bytes
        self.image: PILImage.Image = PILImage.open(image_bytes).convert('RGB')

    def rembg(self) -> bytes:
        image_rembg = remove(self.image, session=SESSION).convert('RGB')
        img_byte_arr = io.BytesIO()
        image_rembg.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr


class Clothing:
    """Describes an article of clothing"""

    def __init__(self, image_bytes: BytesIO):
        """
        Args:
            image_bytes (BytesIO): Image of the clothing item
        """
        self.image_bytes: BytesIO = image_bytes
        self.image: np.ndarray = PILImage.open(image_bytes).convert('RGB')
        self.colors: Colors = None

    def extract_colors(self, n: float = 4):
        """Extract the colors from clothing image

        Args:
            n (float, optional): Number of colors to extract from the image. Defaults to 4.
        """
        # Decompose image into pixels
        pixels = np.array([pixel for row in np.array(self.image) for pixel in row if sum(pixel) != 0])
    
        # Find clusters of colors to determine dominant colors
        color_cluster = KMeans(n_clusters=n, random_state=1, n_init=10).fit(pixels)
        cluster, colors = color_cluster, color_cluster.cluster_centers_
        
        # Compute the percent of the pixels containing that color
        color_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
        (color_hist, _) = np.histogram(cluster.labels_, bins = color_labels)
        color_hist = color_hist.astype("float")
        color_hist /= color_hist.sum()

        # Save the color and the percent of pixels with that color
        image_colors = dict()
        pct_colors = sorted([(percent, color) for percent, color in zip(color_hist, colors)])[::-1]
        for pct, color in pct_colors:
            color = tuple(color.tolist())
            image_colors[color] = pct

        self.colors = image_colors

    def get_colors(self) -> List[Tuple[float, float, float]]:
        """Gets the list of colors as rgb values in order of frequency

        Returns:
            List[Tuple[float, float, float]]: Ordered rgb tuples ordered based on frequency in the image
        """
        colors = [color for color, _ in self.colors.items()]
        return colors

    def get_color_names(self) -> List[str]:
        """Gets the names of the colors as strings in order of frequency

        Returns:
            List[str]: List of color names in order of frequency in the clothing image
        """
        color_names = []
        for color in self.get_colors():
            distance, index = KDT_DB.query(color)
            color_names.append(COLOR_NAMES[index])
        return color_names
