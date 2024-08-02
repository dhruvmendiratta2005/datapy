import cv2 as cv
import numpy as np
from modules import log

def ppath(path, idx=None):
    path_parts = path.split(".")
    if idx is not None:
        path_parts[-2] += f"_{idx}"
    else:
        path_parts[-2] += "_"
    return ".".join(path_parts)

# Grayscale the image
def grayscale(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return gray

# Threshold the image
def threshold(img, threshold_value=180):
    _, thresh = cv.threshold(img, threshold_value, 255, cv.THRESH_BINARY)
    return thresh

# Invert the image
def invert(img):
    inverted = cv.bitwise_not(img)
    return inverted

# Thicken the lines and shapes in the image
def dilate(img):
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    dilated = cv.dilate(img, kernel)
    return dilated

# Perspective transform for each rectangle
def perspective(img, rect, fresh):
    # Get the points of the rectangle
    pts = rect.reshape(4, 2)
    rect_pts = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect_pts[0] = pts[np.argmin(s)]
    rect_pts[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect_pts[1] = pts[np.argmin(diff)]
    rect_pts[3] = pts[np.argmax(diff)]
    
    (tl, tr, br, bl) = rect_pts
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    M = cv.getPerspectiveTransform(rect_pts, dst)
    warped = cv.warpPerspective(fresh, M, (maxWidth, maxHeight))
    
    return warped

# Add padding to the image (10 %)
def add_padding(img):
    h, w = img.shape[:2]
    pad = int(0.1 * h)
    padded = cv.copyMakeBorder(img, pad, pad, pad, pad, cv.BORDER_CONSTANT, value=[255, 255, 255])
    return padded

# Process the image
def process(path):
    img = cv.imread(path)
    img_gray = grayscale(img)
    img_thresh = threshold(img_gray)
    img_invert = invert(img_thresh)
    img_dilate = dilate(img_invert)
    
    fresh = cv.imread(path)
    contours, _ = cv.findContours(img_dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    rects = []
    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            rects.append(approx)

    if not rects:
        log.log("No rectangles found", "warning")
        return []

    processed_paths = []
    for idx, rect in enumerate(rects):
        warped = perspective(img_dilate, rect, fresh)
        padded = add_padding(warped)
        output_path = ppath(path, idx)
        cv.imwrite(output_path, padded)
        processed_paths.append(output_path)

    return processed_paths

