import pytesseract
import cv2

img = cv2.imread('..\\temp\\0.jpg')
d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
n_boxes = len(d['level'])
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

cv2.imwrite('..\\temp\\0.jpg', img)
cv2.waitKey(0)