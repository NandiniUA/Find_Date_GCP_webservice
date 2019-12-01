import os
import datetime
import os
import re
import datefinder #to find the dates in text
from PIL import Image
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify, render_template
from werkzeug.utils import secure_filename
import io
from google.cloud import vision


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="PATH_TO_GOOGLE_CREDENTIALS_JSON_FILE.json"

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    return render_template('index.html', times=dummy_times)

@app.route('/extract_date', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        
		filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        url = os.path.join(app.config['IMAGE_URL'], filename)
		#GOOGLE VISION API CODE for OCR
        client = vision.ImageAnnotatorClient()
        with io.open(url, 'rb') as image_file:
            content = image_file.read()
		
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        os.remove(url)
        text = texts[0].description
        result = text
		
        #below regular expressions are for all date formats
        date_reg_exp = "((?:(1[0-2]|0?[1-9])(-|/|[.])(3[01]|[12][0-9]|0?[1-9])|(3[01]|[12][0-9]|0?[1-9])(-|/|[.])(1[0-2]|0?[1-9]))(-|/|[.])(?:[0-9]{2})?[0-9]{2})"
        months = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|January|February|March|April|May|June|July|August|September|October|November|December|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|january|february|march|april|may|june|july|august|september|october|november|december)"
        #dd(-|/)MMM(-|/)YYYY
        reg1 = "(\d{1,2}[ ]*(-|/)[ ]*"+months+"[ ]*(-|/)[ ]*\d{4})"
        #MMM DD YY
        reg2 = "("+months+"[ ]*\d{1,2}.[ ]*(?:[0-9][0-9])?[0-9][0-9])"
        #MMM DD YYYY
        #reg3 = "("+months+"[ ]*\d{1,2}.[ ]*[1-2][0-9][0-9][0-9])"
        ##YYYY-MM-DD
        reg4 = "[1-2][0-9][0-9][0-9](-|/)[0-3][0-9](-|/)[0-3][0-9]"
        reg_exp = reg1+"|"+date_reg_exp+"|"+reg2+"|"+reg4 #+"|"+reg3
        try:
            m = re.search(reg_exp, text).group(0)
        except AttributeError:
            m = re.search(reg_exp, text)
        if m is not None:
            matches = datefinder.find_dates(m)
            for match in matches:
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resp = jsonify({'date' : match.strftime("%Y-%m-%d")})
                resp.status_code = 201
                return resp
        else:
            resp = jsonify({'date' : None})
            resp.status_code = 201
            return resp
    else:
        resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)