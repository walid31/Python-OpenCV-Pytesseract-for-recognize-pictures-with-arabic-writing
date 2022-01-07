# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import os
import cv2 
import pytesseract
import numpy as np
import re
from pytesseract import Output
from gtts import gTTS
from pathlib import Path
from werkzeug.utils import secure_filename
APP_PATH = Path(__file__).resolve().parent.parent

@blueprint.route('/index')
def index():

    return render_template('index.html', segment='index')

@blueprint.route('/predict', methods = ['POST', 'GET'])
def predict():
    if request.method == 'POST':
        
        image = request.files['image']
        trained_data = request.form['trainedData']
        
        image_name = secure_filename(image.filename)
        img_path = path = os.path.join(APP_PATH.as_posix(), 'base/static/images/' + image_name)
        image.save(img_path)
        img = img_path
        status = predict(img, trained_data)

        if status:
            if trained_data == '1':
                ara_path = os.path.join(APP_PATH.as_posix(), 'base/files/ara.txt')
                text_ara = open(ara_path, 'r', encoding = "utf-8").readlines()
                text_ara = [l for l in text_ara if l != '\n']
                return render_template('index.html', segment='index', text_ara = text_ara, image_name = image_name, trained_data = trained_data, msg = '')
            elif trained_data == '2':
                sii_path = os.path.join(APP_PATH.as_posix(), 'base/files/sii.txt')  
                text_sii = open(sii_path, 'r', encoding = "utf-8")
                return render_template('index.html', segment='index', text_sii = text_sii, image_name = image_name, trained_data = trained_data, msg = '')
            elif trained_data == '3':
                ara_path = os.path.join(APP_PATH.as_posix(), 'base/files/ara.txt') 
                sii_path = os.path.join(APP_PATH.as_posix(), 'base/files/sii.txt')
                text_sii = open(sii_path, 'r', encoding = "utf-8")  
                text_ara = open(ara_path, 'r', encoding = "utf-8")   
                return render_template('index.html', segment='index', text_ara = text_ara, text_sii = text_sii, image_name = image_name, trained_data = trained_data, msg = '')
                    


@blueprint.route('/<template>')
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  




ara_file = os.path.join(APP_PATH.as_posix(), 'base/files/ara.txt')
sii_file = os.path.join(APP_PATH.as_posix(), 'base/files/sii.txt')

def predict(img_path, trained_data):
    img = cv2.imread(img_path)
    img_path = path = os.path.join(APP_PATH.as_posix(), 'base/static/images/image.png')
    cv2.imwrite(img_path, img)
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh=cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    if trained_data == '1':
        
        data = pytesseract.image_to_string(opening,lang='ara')
        
        text_file = open(ara_file, 'w', encoding = "utf-8")
        text_file.write(data)
        text_file.close()
        
        # tts = gTTS(data, lang='ar')
        # tts.save(os.path.join(APP_PATH.as_posix(), 'base/files/ara.mp3'))
    
    elif trained_data == '2':
        
        data=pytesseract.image_to_string(opening,lang='arasii')
        text_file = open(sii_file, 'w', encoding = "utf-8")
        text_file.write(data)
        text_file.close()
       
        # tts = gTTS(data, lang='ar')
        # tts.save(os.path.join(APP_PATH.as_posix(), 'base/files/ara_sii.mp3'))
    
    elif trained_data == '3':
        
        ara = pytesseract.image_to_string(opening,lang='ara')
        sii=pytesseract.image_to_string(opening,lang='arasii')
        
        text_file = open(ara_file, 'w', encoding = "utf-8")
        text_file.write(ara)
        
        text_file = open(sii_file, 'w', encoding = "utf-8")
        text_file.write(sii)
        
        text_file.close()
        
        # tts = gTTS(ara, lang='ar')
        # tts.save(os.path.join(APP_PATH.as_posix(), 'base/files/ara.mp3'))
        # tts = gTTS(sii, lang='ar')
        # tts.save(os.path.join(APP_PATH.as_posix(), 'base/files/sii.mp3'))
    
    return True
    