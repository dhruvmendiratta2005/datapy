import cv2 as cv
import numpy as np
import subprocess
from modules import log

def ppath(path):
    path = path.split(".")
    path [-2] += "_"
    path = ".".join(path)
    return path

def unppath(path):
    path = path.split(".")
    path [-2] = path[-2][:-1]
    path = ".".join(path)
    return path

#Grayscale the image
def grayscale(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    return gray

import cv2 as cv

# Threshold the image
def threshold(img, threshold_value=128):
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
    
    # save the warped image
    cv.imwrite(path, padded)

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

    cv.imshow("Table", combined)
    cv.waitKey(0)

    #subtract the lines from the image
    combined = cv.subtract(img, combined)

    #remove noise and dilate the image
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    combined = cv.erode(combined, kernel, iterations=1)
    combined = cv.dilate(combined, kernel, iterations=1)

    return combined

#dilate the words and turn them into horizontal smudges.
def dilate_words(img):

    #self.dilated_image = cv2.dilate(self.thresholded_image, kernel_to_remove_gaps_between_words, iterations=5)
    #simple_kernel = np.ones((5,5), np.uint8)
    #self.dilated_image = cv2.dilate(self.dilated_image, simple_kernel, iterations=2)

    # Create a kernel
    kernel = np.array([
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1]
    ])

    dilated = cv.dilate(img, kernel, iterations=5)

    simple_kernel = np.ones((5,5), np.uint8)
    dilated = cv.dilate(dilated, simple_kernel, iterations=2)

    return dilated

# find all these smudges using the findContours method and draw them on the original image
def find_words(img, path):
    fresh = cv.imread(path)
    result = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = result[0] if len(result) == 2 else result[1]
    
    bounding_boxes = []
    image_with_all_bounding_boxes = fresh.copy()

    #Convert The Blobs Into Bounding Boxes : reduces it to a box that can fully enclose the contour shape
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        bounding_boxes.append((x, y, w, h))
        image_with_all_bounding_boxes = cv.rectangle(image_with_all_bounding_boxes, (x, y), (x+w, y+h), (0, 255, 0), 2)

    #Draw The Bounding Boxes On The Original Image
    for x, y, w, h in bounding_boxes:
        fresh = cv.rectangle(fresh, (x, y), (x+w, y+h), (0, 255, 0), 2)

    #process the bounding boxes ocr
    mean_height = get_mean_height_of_bounding_boxes(bounding_boxes)
    bounding_boxes = sort_bounding_boxes_by_y_coordinate(bounding_boxes)
    rows = club_all_bounding_boxes_by_similar_y_coordinates_into_rows(bounding_boxes, mean_height)
    rows = sort_all_rows_by_x_coordinate(rows)
    table = crop_each_bounding_box_and_ocr(rows, fresh)

    print(table)
    return fresh

#get_mean_height_of_bounding_boxes
def get_mean_height_of_bounding_boxes(bounding_boxes):
    heights = []
    for x, y, w, h in bounding_boxes:
        heights.append(h)
    return np.mean(heights)

#sort_bounding_boxes_by_y_coordinate
def sort_bounding_boxes_by_y_coordinate(bounding_boxes):
    return sorted(bounding_boxes, key=lambda x: x[1])

#club_all_bounding_boxes_by_similar_y_coordinates_into_rows
def club_all_bounding_boxes_by_similar_y_coordinates_into_rows(bounding_boxes, mean_height):
    rows = []
    half_of_mean_height = mean_height / 2
    current_row = [bounding_boxes[0]]
    for bounding_box in bounding_boxes[1:]:
        current_bounding_box_y = bounding_box[1]
        previous_bounding_box_y = current_row[-1][1]
        distance_between_bounding_boxes = current_bounding_box_y - previous_bounding_box_y
        if distance_between_bounding_boxes < half_of_mean_height:
            current_row.append(bounding_box)
        else:
            rows.append(current_row)
            current_row = [bounding_box]
    rows.append(current_row)

    return rows

def sort_all_rows_by_x_coordinate(rows):
    for row in rows:
        row.sort(key=lambda x: x[0])
    return rows

def crop_each_bounding_box_and_ocr(rows, fresh):
    table = []
    current_row = []
    image_number=0
    for row in rows:
        for bouding_box in row:
            x, y, w, h = bouding_box
            y = y - 5
            cropped_image = fresh[y:y+h+5, x:x+w]
            image_slice_path = "temp/$"+str(image_number)+".jpg"
            cv.imwrite(image_slice_path, cropped_image)

            results_from_ocr = ocr(image_slice_path)
            current_row.append(results_from_ocr)
            image_number += 1
        table.append(current_row)
        current_row = []
    return table

def ocr(image_path):
    output = subprocess.getoutput('tesseract ' + image_path + ' - -l eng --oem 3 --psm 7 --dpi 72 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789().calmg* "')
    output = output.strip()
    return output


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

    cv.imshow("Processed Image", img)
    cv.waitKey(0)

    # Dilate the image
    img = dilate(img)

    # Find the contours and apply perspective transform
    img = perspective(img, path)

    # Add padding to the image
    img = add_padding(img, path)

    cv.imshow("Processed Perspective", img)
    cv.waitKey(0)

    # Erode the vertical lines
    img = erode_lines(img)

    # Dilate the words
    img = dilate_words(img)
    cv.imshow("Processed Words", img)
    cv.waitKey(0)
    # Find the words
    img = find_words(img, path)

    cv.imshow("Processed Image", img)
    cv.waitKey(0)

    cv.imwrite(ppath(path), img)


    return img