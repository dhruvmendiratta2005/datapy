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
num_pages, pdf_to_image = image.pdf_to_image(filename)
if pdf_to_image:
    log.log("Pdf converted to image successfully", "success")
else:
    sys.exit(1)

# Process every image in the folder
log.log("Processing images", "info")

#get the number of pages in the pdf
for i in range(num_pages):
    log.log("Processing page "+str(i+1), "info")
    proc.process("temp/"+str(i)+".jpg")
