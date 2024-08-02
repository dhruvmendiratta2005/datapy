import cv2
import numpy as np

# Load image, convert to grayscale, Gaussian blur, Otsu's threshold
image = cv2.imread('temp/0_27.jpg')
original = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours
cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]

# Define area threshold for filtering contours
AREA_THRESHOLD = 100

# Iterate through contours
for c in cnts:
    area = cv2.contourArea(c)
    if area < AREA_THRESHOLD:
        continue

    # Approximate the contour to a polygon and check if it is a rectangle
    epsilon = 0.02 * cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, epsilon, True)
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        if 0.9 <= aspect_ratio <= 1.1:  # Check if the contour is approximately square
            # Check if the checkbox is filled
            mask = np.zeros(gray.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mean_val = cv2.mean(gray, mask=mask)[0]
            if mean_val < 200:  # If the mean value is low, the checkbox is filled
                
                # Text to be written
                text = "YES"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8  # Increase the font size
                font_thickness = 2
                text_color = (0, 0, 0)  # Green text
                bg_color = (255, 255, 255)  # Black background

                # Calculate text size
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
                text_x = x
                text_y = y + h

                # Draw the background rectangle
                cv2.rectangle(original, (text_x, text_y - text_height - baseline), (text_x + text_width, text_y + baseline), bg_color, cv2.FILLED)

                # Put the text on the image
                cv2.putText(original, text, (text_x, text_y), font, font_scale, text_color, font_thickness)

            else:

                # Text to be written
                text = "NO"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8  # Increase the font size
                font_thickness = 2
                text_color = (0, 0, 0)  # Green text
                bg_color = (255, 255, 255)  # Black background

                # Calculate text size
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
                text_x = x
                text_y = y + h

                # Draw the background rectangle
                cv2.rectangle(original, (text_x, text_y - text_height - baseline), (text_x + text_width, text_y + baseline), bg_color, cv2.FILLED)

                # Put the text on the image
                cv2.putText(original, text, (text_x, text_y), font, font_scale, text_color, font_thickness)

# Display the result
cv2.imshow('Result', original)
cv2.waitKey(0)
cv2.destroyAllWindows()