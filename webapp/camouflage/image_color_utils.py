import numpy as np
from sklearn.cluster import KMeans


def visualize_Dominant_colors(C_hist, C_centroids):
    rect_color = []
    height, width = 50, 300
    img_colors = sorted([(percent, color) for (percent, color) in zip(C_hist, C_centroids)])
    for (percent, color) in img_colors:
        color = color.astype("uint8").tolist()
        color = [c / 255.0 for c in color]
        color_width = int(percent * width)
        color_rect = np.zeros([height, color_width, 3])
        color_rect = np.full_like(color_rect, color)
        rect_color.append(color_rect)
    return np.concatenate(rect_color, axis=1)


def dom_colors(image):
    pixels = np.array([pixel for row in image for pixel in row if sum(pixel) != 0])
    
    # Find clusters of colors to determine dominant colors
    n = 4
    color_cluster = KMeans(n_clusters=n, random_state=1).fit(pixels)
    cluster, colors = color_cluster, color_cluster.cluster_centers_
    
    # Compute the percent of the pixels containing that color
    color_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (color_hist, _) = np.histogram(cluster.labels_, bins = color_labels)
    color_hist = color_hist.astype("float")
    color_hist /= color_hist.sum()
    rect_color = visualize_Dominant_colors(color_hist,  color_cluster.cluster_centers_)

    # Save the color and the percent of pixels with that color
    img_colors = sorted(list(zip(color_hist, colors)))[::-1]

    return img_colors, rect_color


def colors(image):
    """
    Get the color(s) of the single clothing item in the image
    """
    colors, rect_color = dom_colors(image)
    return colors, rect_color