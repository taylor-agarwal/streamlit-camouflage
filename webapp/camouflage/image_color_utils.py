import numpy as np
import cv2
from sklearn.cluster import KMeans


def visualize_Dominant_colors(cluster, C_centroids):
    C_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (C_hist, _) = np.histogram(cluster.labels_, bins = C_labels)
    C_hist = C_hist.astype("float")
    C_hist /= C_hist.sum()

    rect_color = np.zeros((50, 300, 3), dtype=np.uint8)
    img_colors = sorted([(percent, color) for (percent, color) in zip(C_hist, C_centroids)])
    start = 0
    for (percent, color) in img_colors:
        end = start + (percent * 300)
        cv2.rectangle(rect_color, (int(start), 0), (int(end), 50), \
                      color.astype("uint8").tolist(), -1)
        start = end
    return rect_color


def dom_colors(image):
    # To eliminate noise
    n = 4
    
    height, width, _ = image.shape
    
    # Extract the middle third of the image
    pixels = image[(height // 3):(2*height // 3),
                   (width // 3):(2*width // 3),
                   :]
    pixels = np.array([pixel for row in pixels for pixel in row])
    
    # Find clusters of colors to determine dominant colors
    color_cluster = KMeans(n_clusters=n, random_state=1).fit(pixels)
    cluster, colors = color_cluster, color_cluster.cluster_centers_
    rect_color = visualize_Dominant_colors(cluster,  color_cluster.cluster_centers_)
    
    # Compute the percent of the pixels containing that color
    color_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (color_hist, _) = np.histogram(cluster.labels_, bins = color_labels)
    color_hist = color_hist.astype("float")
    color_hist /= color_hist.sum()

    # Save the color and the percent of pixels with that color
    img_colors = sorted(list(zip(color_hist, colors)))[::-1]

    return img_colors, rect_color


def colors(image):
    """
    Get the color(s) of the single clothing item in the image
    """
    colors, rect_color = dom_colors(image)
    return colors, rect_color