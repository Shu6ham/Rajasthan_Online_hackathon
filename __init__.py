#!/usr/bin/python3
'''
IMPORTS :

 1. Flask from flask
 2. getting_label_file -----> to capture photo and get labels of th image
 3.
'''
# Imports

import time
from flask import Flask,render_template,request
import mysql.connector as mysql
import cv2
import kairos_face as kf
import matplotlib.pyplot as plt
import json
from gtts import gTTS
import os
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

# kairos key and id
kf.settings.app_id = 'ed6e261d'
kf.settings.app_key = 'bfe71f59834f765f8b215a06e9861434'

# connect to mysql database
conn = mysql.connect(user='root', password='1289', database='flask', host='localhost')
cursor = conn.cursor()

app = Flask(__name__)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

@app.route('/register')
def register():
    # speak messages
    os.system("mpg321 register.wav")
    os.system("mpg321 pic_not.wav")

    # register page--->enter details---->that will be sent to image_cap
    return render_template('register.html')

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

@app.route('/image_cap', methods=['GET', 'POST'])
# to insert values obtained from register page to database
def image_cap():
    print('entered')
    if request.method == 'POST':
        # get data from register form
        name = request.form['name']
        number = int(request.form['number'])
        email = request.form['email']
        password = request.form['password']

        # capture image---> save----> release cam
        cam = cv2.VideoCapture(0)
        frame = cam.read()[1]
        cv2.imwrite('face.jpg',frame)
        cam.release()

        # enroll face with subject id  email
        enrolled_face = kf.enroll_face(file='face.jpg', subject_id=str(email), gallery_name='a-gallery')
        # get face id
        face_id=enrolled_face['face_id']
        # status T/F face enrlled or not
        status = enrolled_face['images'][0]['transaction']['status']
        if status=="success":
            # execute query to insert data
            out = cursor.execute('insert into flask_use values("%s","%d","%s","%s","%s")'%(name,number,email,password,face_id))
            conn.commit()
            return render_template('image_cap.html')
        else:
            return '<h1>Non-Human detected</h1>'


#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

@app.route('/login')
def login():

    # Playing the converted fil
    os.system("mpg321 login.wav")
    os.system("mpg321 pic_verf.wav")
    return render_template('login.html')

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if request.method == 'POST':
        print("<h1>in file</h1>")
        # capture photo
        cam = cv2.VideoCapture(0)
        frame = cam.read()[1]
        cv2.imwrite('face2.jpg',frame)
        cam.release()

        # get data from lgin form
        emaill = request.form['email']
        passwordd = request.form['password']

        # verify email and password from db
        cursor.execute('select * from flask_use where email="%s" and password="%s"'%(emaill,passwordd))
        login_details = cursor.fetchall()

        # face login recognize_face
        recognized_faces = kf.recognize_face(file='face2.jpg', gallery_name='a-gallery')
        status = recognized_faces['images'][0]['transaction']['status']

        # if data not found in db
        if len(login_details)==0:
            return '<h1>Unregistered E-mail or Password</h1>'
        # data found in db
        else:
            # if face recognized
            if status=="success":
                os.system("mpg321 dash.wav")
                return render_template('dashboard.html')
            # face not recognized
            elif status=="failure":
                os.system("mpg321 not_reg.wav")
                return "<h1>Face not registered</h1>"
            else:
                return "Error please retry"
    else:
        return 'sss'

@app.route('/result', methods=['GET','POST'])
def result():
    if request.method == 'POST':
        # get data from dashboard
        company = request.form['company']
        open = float(request.form['open'])
        high = float(request.form['high'])
        low = float(request.form['low'])
        adj = float(request.form['adj'])
        volume = float(request.form['volume'])
        #-----------------------------------------------------------------------------
        # functions to read data from csv----->train data----->predict
        def apple():
            df = pd.read_csv('Apple.csv')
            train_data = df[['Open','High','Low','Adj Close','Volume']]
            train_target = df[['Close']]

            # Create linear regression object
            regr = linear_model.LinearRegression()

            # Train the model using the training sets
            regr.fit(train_data,train_target)

            # Make predictions using the testing set-------2d required
            #y_pred = regr.predict(df[['Open','High','Low','Adj Close','Volume']])
            y_pred = regr.predict([[open,high,low,adj,volume]])
            return round(y_pred[0][0],3)


        def reliance():
            df = pd.read_csv('reliance.csv')
            df = df.dropna(subset=['Open','High','Low','Adj Close','Volume','Close'])
            train_data = df[['Open','High','Low','Adj Close','Volume']]
            train_target = df[['Close']]

            # Create linear regression object
            regr = linear_model.LinearRegression()

            # Train the model using the training sets
            regr.fit(train_data,train_target)

            # Make predictions using the testing set-------2d required
            #y_pred = regr.predict(df[['Open','High','Low','Adj Close','Volume']])
            y_pred = regr.predict([[open,high,low,adj,volume]])
            return round(y_pred[0][0],3)


        def infosis():
            df = pd.read_csv('infosis.csv')
            df = df.dropna(subset=['Open','High','Low','Adj Close','Volume','Close'])
            train_data = df[['Open','High','Low','Adj Close','Volume']]
            train_target = df[['Close']]

            # Create linear regression object
            regr = linear_model.LinearRegression()

            # Train the model using the training sets
            regr.fit(train_data,train_target)

            # Make predictions using the testing set-------2d required
            #y_pred = regr.predict(df[['Open','High','Low','Adj Close','Volume']])
            y_pred = regr.predict([[open,high,low,adj,volume]])
            return round(y_pred[0][0],3)


        def tcs():
            df = pd.read_csv('tcs.csv')
            df = df.dropna(subset=['Open','High','Low','Adj Close','Volume','Close'])
            train_data = df[['Open','High','Low','Adj Close','Volume']]
            train_target = df[['Close']]

            # Create linear regression object
            regr = linear_model.LinearRegression()

            # Train the model using the training sets
            regr.fit(train_data,train_target)

            # Make predictions using the testing set-------2d required
            #y_pred = regr.predict(df[['Open','High','Low','Adj Close','Volume']])
            y_pred = regr.predict([[open,high,low,adj,volume]])
            return round(y_pred[0][0],3)

        # initial closing price
        close_price = 0

        # message---->get price from functions---->speak closing price--->show result
        if company=='Apple':
            os.system("mpg321 apple.wav")
            close_price = apple()
            myobj = gTTS(text="the closing price should be "+str(close_price)+" US Dollars", lang='en', slow=True)
            myobj.save("res.wav")
            os.system("mpg321 res.wav")
            return render_template('result_apple.html', variable = "$ "+str(close_price))

        elif company=='Tcs':
            os.system("mpg321 tcs.wav")
            close_price = tcs()
            myobj = gTTS(text="the closing price should be "+str(close_price)+" US Dollars", lang='en', slow=True)
            myobj.save("res.wav")
            os.system("mpg321 res.wav")
            return render_template('result_tcs.html', variable = "$ "+str(close_price))

        elif company=='Infosis':
            os.system("mpg321 infosis.wav")
            close_price = infosis()
            myobj = gTTS(text="the closing price should be "+str(close_price)+" US Dollars", lang='en', slow=True)
            myobj.save("res.wav")
            os.system("mpg321 res.wav")
            return render_template('result_infosis.html', variable = "$ "+str(close_price))

        else:
            os.system("mpg321 reliance.wav")
            close_price = reliance()
            myobj = gTTS(text="the closing price should be "+str(close_price)+" US Dollars", lang='en', slow=True)
            myobj.save("res.wav")
            os.system("mpg321 res.wav")
            return render_template('result_reliance.html', variable = "$ "+str(close_price))

    else:
        return 'ERROR OCCURED'



#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

if __name__ == '__main__':
    # run application
    app.run(host='0.0.0.0',port=9999)
