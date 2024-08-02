import cv2
import requests
from PIL import Image
from docx import Document
import numpy as np

def do(filename, output_filename):
    # Load the image
    image = cv2.imread(filename)

    # Check if image was loaded
    if image is None:
        print("Error: Image not found.")
        return

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoise the image
    denoised_image = cv2.fastNlMeansDenoising(gray_image)

    # Save the processed image temporarily
    temp_image_path = "temp_image.png"
    cv2.imwrite(temp_image_path, denoised_image)

    # OCR.Space API configuration
    api_key = 'K82325263088957'  # Replace with your OCR.Space API key
    url = 'https://api.ocr.space/parse/image'

    # Prepare the API request
    with open(temp_image_path, 'rb') as image_file:
        files = {'file': image_file}
        data = {'apikey': api_key, 'language': 'eng'}

        # Call the OCR.Space API
        response = requests.post(url, files=files, data=data)
        result = response.json()

    # Check the response for errors
    if result['OCRExitCode'] == 1:
        extracted_text = result['ParsedResults'][0]['ParsedText']
        print("Extracted Text: ", extracted_text)

        # Save the extracted text to a Word document
        doc = Document()
        doc.add_heading('Extracted Text', level=1)
        doc.add_paragraph(extracted_text)

        # Save the document
        doc.save(output_filename)
        print(f"Text saved to {output_filename}")
    else:
        print("Error in OCR processing:", result['ErrorMessage'])