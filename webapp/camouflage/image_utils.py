from PIL import Image
import numpy as np
from rembg import remove
from typing import Dict


def extract_clothes(image_bytes) -> Dict[str, np.ndarray]:
    """
    Extracts clothes from the file. Up to 9 clothing items per image, three across and three down
    Args:
        path: Image file path
    """
    img = Image.open(image_bytes).convert('RGB')

    img_rembg = remove(img).convert('RGB')
    images = {
        "cropped": np.array(img_rembg), 
        "original": np.array(img)
    }

    return images