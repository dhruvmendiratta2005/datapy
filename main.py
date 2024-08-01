import sys
from modules import log
from core import image, proc

if len(sys.argv) < 2:
    log.log("Usage: python main.py <filename>", "error")
    sys.exit(1)
    
filename = sys.argv[1]

#Check if valid filename
if not filename.endswith(".pdf"):
    log.log("Invalid file format. Please provide a .pdf file", "error")
    sys.exit(1)

#Check if file exists
try:
    with open(filename, "r") as file:
        log.log("File "+filename+" found", "info")
except FileNotFoundError:
    log.log("File "+filename+" not found", "error")
    sys.exit(1)

#Convert pdf to image
log.log("Converting pdf to image", "info")
if image.pdf_to_image(filename):
    log.log("Pdf converted to image successfully", "success")
else:
    sys.exit(1)

proc.process("temp/0.jpg")
