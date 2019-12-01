#got accuracy of 533/595 = 89.57%
# import the necessary packages
from PIL import Image
from dateparser.search import search_dates
from datetime import *
import pytesseract
import argparse
import cv2
import datefinder
import os
import re
import io
from google.cloud import vision
import glob

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="PATH_TO_GOOGLE_CREDENTIALS_JSON_FILE.json"
folder = "/folder_containing_photos"
path = []
for filename in os.listdir(folder):
    path.append( os.path.join(folder,filename))
print(len(path))

count = 0
for p in path:
    print(p)
    client = vision.ImageAnnotatorClient()
    path = p
    with io.open(path, 'rb') as image_file:
            content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    try:
        in_str = texts[0].description
    except IndexError:
        in_str = 'null'
    #print(in_str)
    #print(type(in_str))
    text = in_str

    #orig created
    #reg_exp = "(\d{1,2}[ ]*-[ ]*[a-zA-Z]{3}[ ]*-[ ]*\d{4})|([0-3]?[0-9]/[0-3]?[0-9]/(?:[0-9][0-9])?[0-9][0-9])|([a-zA-Z]{3}[ ]*\d{1,2}.[ ]*\d{4})"

    #below are for all date formats
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

    #reg_exp = "(\d{1,2}[ ]*-[ ]*[a-zA-Z]{3}[ ]*-[ ]*\d{4})|((?:(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])|(3[01]|[12][0-9]|0?[1-9])/(1[0-2]|0?[1-9]))/(?:[0-9]{2})?[0-9]{2})|([a-zA-Z]{3}[ ]*\d{1,2}.[ ]*[1-2][0-9][0-9][0-9])"
    #m = re.search('([0-3][0-9]/[0-3][0-9]/(?:[0-9][0-9])?[0-9][0-9])|(\d{1,2}-[a-zA-Z]{3}-\d{4})', text).group(0)
    
    try:
        m = re.search(reg_exp, text).group(0)
    except AttributeError:
        m = re.search(reg_exp, text)

    if m is not None:
        #print(m)
        #print(type(m))
        matches = datefinder.find_dates(m)
        for match in matches:
            print(match)
            count = count + 1
            print(count)

print(count)



