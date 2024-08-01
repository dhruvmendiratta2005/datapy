import cv2 as cv
import numpy as np
from modules import log

def ppath(path):
    path = path.split(".")
    path [-2] += "_"
    path = ".".join(path)
    return path

#Grayscale the image
def grayscale(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    return gray

import cv2 as cv

# Threshold the image
def threshold(img, threshold_value=100):
    # For example, using a threshold value of 128
    _, thresh = cv.threshold(img, threshold_value, 255, cv.THRESH_BINARY)

    return thresh

# Invert the image
def invert(img):
    # Invert the image
    inverted = cv.bitwise_not(img)

    return inverted

#Here we are going to make all the lines and any shapes in the image thicker. This will help us to correctly identify the “contours” and hopefully the “contour” that makes up the largest box. We are hoping that the largest box is the table.
def dilate(img):
    # Create a kernel
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))

    # Dilate the image
    dilated = cv.dilate(img, kernel)

    return dilated

# Find the contours
def perspective(img, path):
    fresh = cv.imread(path)
    # Find the contours
    contours, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # filter out the contours that are not rectangles
    rects = []
    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            rects.append(approx)

    # find the largest rectangle
    largest = None
    largest_area = 0
    for rect in rects:
        area = cv.contourArea(rect)
        if area > largest_area:
            largest = rect
            largest_area = area

    #DRAW THE RECTANGLE
    cv.drawContours(fresh, [largest], -1, (0, 255, 0), 3)
    cv.imshow('image', fresh)
    cv.waitKey(0)

    # perspective transform to the largest rectangle
    if largest is not None:
        # get the points of the rectangle
        pts = largest.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        # the top-left point has the smallest sum
        # the bottom-right point has the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        # the top-right point has the smallest difference
        # the bottom-left point has the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        # get the width and height of the rectangle
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # get the destination points
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        
        # get the perspective transform matrix
        M = cv.getPerspectiveTransform(rect, dst)
        
        # warp the image
        warped = cv.warpPerspective(fresh, M, (maxWidth, maxHeight))
        
        # return the warped image
        return warped
    else:
        log.log("No rectangle found", "warning")
        return fresh
    
# add padding to the image (10 %)
def add_padding(img, path):
    # get the dimensions of the image
    h, w = img.shape[:2]
    
    # calculate the padding
    pad = int(0.1 * h)
    
    # add the padding
    padded = cv.copyMakeBorder(img, pad, pad, pad, pad, cv.BORDER_CONSTANT, value=[255, 255, 255])

    return padded

def erode_horizontal_lines(img):

    ver = np.array([[1],
            [1],
            [1],
            [1],
            [1],
            [1],
            [1]])
    
    eroded = cv.erode(img, ver, iterations=10)
    
    return eroded

def erode_vertical_lines(img):
    # Create a vertical kernel
    kernel_size = (1, 7)  # Adjust the kernel size as needed
    kernel = np.ones(kernel_size, np.uint8)

    # Perform erosion
    eroded = cv.erode(img, kernel, iterations=10)  # Adjust the number of iterations as needed

    return eroded

def erode_lines(img):
    img = grayscale(img)
    img = threshold(img)
    img = invert(img)

    hori = erode_horizontal_lines(img)
    vert = erode_vertical_lines(img)

    combined = cv.add(hori, vert)

    #dilate_combined_image_to_make_lines_thicker
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    combined = cv.dilate(combined, kernel, iterations=5)

    #subtract the lines from the image
    combined = cv.subtract(img, combined)

    #remove noise and dilate the image
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    combined = cv.erode(combined, kernel, iterations=1)
    combined = cv.dilate(combined, kernel, iterations=1)

    return combined

# Process the image
def process(path):

    # Read the image
    img = cv.imread(path)

    # Convert the image to grayscale
    img = grayscale(img)

    # Threshold the image
    img = threshold(img)

    # Invert the image
    img = invert(img)

    # Dilate the image
    img = dilate(img)

    # Find the contours and apply perspective transform
    img = perspective(img, path)

    #FIX PERSPECTIVE
    cv.imshow('image', img)
    cv.waitKey(0)

    # Add padding to the image
    img = add_padding(img, path)

    cv.imwrite(ppath(path), img)

    return ppath(path)