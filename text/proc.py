import cv2 as cv
import numpy as np

def ppath(path, idx=None):
    #idx is the index of the image
    path_parts = path.split(".")
    if idx is not None:
        path_parts[-2] += f"${idx}"
    else:
        path_parts[-2] += "$"
    return ".".join(path_parts)

# Grayscale the image
def grayscale(img):
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Threshold the image
def threshold(img, threshold_value=180):
    _, thresh = cv.threshold(img, threshold_value, 255, cv.THRESH_BINARY)
    return thresh

# Invert the image
def invert(img):
    return cv.bitwise_not(img)

# Thicken the lines and shapes in the image
def dilate(img):
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    return cv.dilate(img, kernel)

# Remove tables from the image
def remove_tables(img, img_dilate):
    contours, _ = cv.findContours(img_dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # Create a single-channel mask for the tables
    mask = np.ones(grayscale(img).shape, dtype=np.uint8) * 255  # Start with a white mask

    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.02 * peri, True)
        
        # Check if the contour is a rectangle (table)
        if len(approx) == 4:
            cv.drawContours(mask, [approx], -1, (0), thickness=cv.FILLED)  # Fill the rectangle in the mask with black

    # Use the mask to remove tables from the original image
    img_no_tables = cv.bitwise_and(img, img, mask=mask)
    img_no_tables[mask == 0] = (255, 255, 255)  # Replace the table areas with white
    return img_no_tables

# Process the image
def process(path):
    img = cv.imread(path)
    img_gray = grayscale(img)
    img_thresh = threshold(img_gray)
    img_invert = invert(img_thresh)
    img_dilate = dilate(img_invert)

    # Remove tables from the image
    img_no_tables = remove_tables(img, img_dilate)

    # Optionally, you can return or save the processed image without tables
    output_path = ppath(path)
    cv.imwrite(output_path, img_no_tables)
    
    return output_path
