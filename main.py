from img2table.document import PDF
from img2table.ocr import TesseractOCR

# Instantiation of the pdf
pdf = PDF(src="tests\\table.pdf")

# Instantiation of the OCR, Tesseract, which requires prior installation
ocr = TesseractOCR(lang="eng")

# Table identification and extraction
pdf_tables = pdf.extract_tables(ocr=ocr)

# We can also create an excel file with the tables
pdf.to_xlsx('tables.xlsx',
            ocr=ocr)
