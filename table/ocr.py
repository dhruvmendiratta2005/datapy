from img2table.document import Image
from img2table.ocr import TesseractOCR

def do(path):
    img = Image(src=path)

    # Instantiation of the OCR, Tesseract, which requires prior installation
    ocr = TesseractOCR(lang="eng")

    # Table identification and extraction
    img_tables = img.extract_tables(ocr=ocr)

    # Display the extracted tables. There is a pandas DataFrame representation of the table so you can just get its shape table.df.shape
    for table in img_tables:
        print(table.df)
        print(table.df.shape)
