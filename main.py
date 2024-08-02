# app.py
from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import os
import shutil
from werkzeug.utils import secure_filename
from modules import log
from table import image, proc, ocr
import text
import text.ocr
import text.proc

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.secret_key = 'supersecretkey'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('process_file', filename=filename))
    else:
        flash('Invalid file format. Please upload a PDF file.')
        return redirect(request.url)

@app.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    log.log("Converting pdf to image", "info")
    num_pages = image.pdf_to_images(filepath)
    if num_pages > 0:
        log.log("Pdf converted to image successfully", "success")
    else:
        flash('Error converting PDF to images')
        return redirect(url_for('index'))

    if not os.path.exists("publish"):
        os.makedirs("publish")
    else:
        for file in os.listdir("publish"):
            os.remove("publish/"+file)

    log.log("Processing images", "info")
    processed = []
    for i in range(num_pages):
        log.log("Processing page "+str(i+1), "info")
        processed.append(proc.process("temp/"+str(i)+".jpg"))
        log.log("Page "+str(i+1)+" processed successfully", "success")

    log.log("Doing OCR for tables", "info")
    for i in range(num_pages):
        log.log("Processing page "+str(i+1), "info")
        processed[i] = ocr.do("temp/"+str(i)+".jpg")
        log.log("Page "+str(i+1)+" processed successfully", "success")

    log.log("OCR done", "info")

    log.log("Doing OCR for text", "info")
    for i in range(num_pages):
        log.log("Processing page "+str(i+1), "info")
        text.proc.process("temp/"+str(i)+".jpg")
        text.ocr.do("temp/"+str(i)+"$.jpg", "publish/page_"+str(i+1)+".docx")

    for file in os.listdir("temp"):
        os.remove("temp/"+file)
    os.rmdir("temp")

    log.log("Temp folder deleted", "info")

    shutil.make_archive("publish", 'zip', "publish")
    log.log("Publish folder zipped", "info")

    for file in os.listdir("publish"):
        os.remove("publish/"+file)
    os.rmdir("publish")

    log.log("Publish folder deleted", "info")

    log.log("Process completed", "success")

    return send_file('publish.zip', as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0')
