import sys

import cv2
import numpy as np


def auto_canny(image, sigma=0.33):
    """
    Detect image edge via Canny Function.

    :param image: ndarray, dtpye=np.uint8
    :param sigma: float
    :return: ndarray edged image
    """

    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    return edged


def remove_noise(image, lower, upper):
    """
    Remove noise from image.

    :param image: ndarray
    :param lower: int
    :param upper: int
    :return:
    """
    drawing = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i, j] < lower:
                drawing[i, j] = 0
            elif image[i, j] > upper:
                drawing[i, j] = 255
            else:
                drawing[i, j] = image[i, j]
    return drawing


def find_clearance(file_path):
    """
    Return (Side, Clearance) for a image.
    :param file_path: String, image path
    :return: none
    """
    img = np.loadtxt(file_path)  # read content from input file
    img_remove_noise = remove_noise(img, 1, 4)
    img_canny = auto_canny(cv2.GaussianBlur(img_remove_noise, (5, 5), 0))
    img_dilate = cv2.dilate(img_canny, None, iterations=2)
    img_erode = cv2.erode(img_dilate, None, iterations=2)
    cropped = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    cropped[30:108, 60:120] = img_erode[30:108, 60:120]  # get the interested region

    img_contours, contours, hierarchy = cv2.findContours(cropped, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    contours_poly = [None] * len(contours)
    bound_rect = [None] * len(contours)
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        bound_rect[i] = cv2.boundingRect(contours_poly[i])

    left = bound_rect[0][0] - 60
    right = 120 - (bound_rect[0][0] + bound_rect[0][2])
    print("left", left * 1.5 / 60) if (left > right) else print("right", right * 1.5 / 60)


if __name__ == '__main__':

    try:
        path = sys.argv[1]
    except IndexError:
        print("Please provide valid file path")

    find_clearance(sys.argv[1])
