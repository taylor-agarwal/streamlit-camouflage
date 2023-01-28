from PIL import Image
import cv2
import numpy as np


def extract_clothes(image_bytes):
    """
    Extracts clothes from the file. Up to 9 clothing items per image, three across and three down
    Args:
        path: Image file path
    """
    img = Image.open(image_bytes).convert('RGB')
    image = np.array(img)
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Image width and height
    height = image.shape[0]
    width = image.shape[1]

    # Find contours, obtain bounding box, extract and save ROI
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    
    # Slice images of clothes out of the image
    clothing_images = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        if w > (width / 4) or h > (height / 4):
            clothing_image = original[y:y+h, x:x+w]
            clothing_images.append(clothing_image)
    
    # Check if the original is already in the images
    if any([np.array_equal(original, image) for image in clothing_images]):
        return clothing_images

    # Otherwise return the original with the other images
    return [original] + clothing_images