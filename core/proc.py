import cv2 as cv

def ppath(path):
    path = path.split(".")
    path [-2] += "_"
    path = ".".join(path)
    return path

#Grayscale the image
def grayscale(path):
    img = cv.imread(path)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    #save the image
    path = ppath(path)

    cv.imwrite(path, gray)

import cv2 as cv

# Threshold the image
def threshold(path):
    # Read the image
    img = cv.imread(path)

    # Use a different thresholding method
    # You can try a fixed threshold value instead of Otsu's method
    # For example, using a threshold value of 128
    threshold_value = 128
    _, thresh = cv.threshold(img, threshold_value, 255, cv.THRESH_BINARY)

    # Save the thresholded image
    cv.imwrite(path, thresh)

# Invert the image
def invert(path):
    # Read the image
    img = cv.imread(path)

    # Invert the image
    inverted = cv.bitwise_not(img)

    # Save the inverted image
    cv.imwrite(path, inverted)

#Here we are going to make all the lines and any shapes in the image thicker. This will help us to correctly identify the “contours” and hopefully the “contour” that makes up the largest box. We are hoping that the largest box is the table.
def dilate(path):
    # Read the image
    img = cv.imread(path)

    # Create a kernel
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))

    # Dilate the image
    dilated = cv.dilate(img, kernel)

    # Save the dilated image with a prefix
    cv.imwrite(path, dilated)


def process(path):
    grayscale(path)

    path = ppath(path)

    threshold(path)
    invert(path)
    dilate(path)
    return path

process("../temp/0.jpg")