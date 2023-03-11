from PIL import Image
import numpy as np
from rembg import remove, new_session
from typing import Dict

SESSION = new_session("u2netp")

def extract_clothes(image_bytes) -> Dict[str, np.ndarray]:
    """
    Extracts clothes from the file. Up to 9 clothing items per image, three across and three down
    Args:
        path: Image file path
    """
    img = Image.open(image_bytes).convert('RGB')
    img = remove(img, session=SESSION).convert('RGB')
    images = {
        "cropped": np.array(img)
    }

    return images