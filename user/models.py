from msilib.schema import tables
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,session
import uuid
from passlib.hash import pbkdf2_sha256
import cv2
from datetime import datetime
import os
import face_recognition
import time
import numpy as np
import pandas as pd
from requests import Response



class User:
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        
        return jsonify(user), 200

    def signup(self, db):
        user = {
            '_id': uuid.uuid4().hex,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'subject': request.form.get('subject'),
        }

        # encrypt the password
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # check if user already exists
        if db.users.find_one({'email': user['email']}):
            return jsonify({'error': 'User already exists'}), 400
        
        # start session
        if db.users.insert_one(user):
            return self.start_session(user)
        
        return jsonify(user), 200

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self, db):

        user = db.users.find_one({'email': request.form.get('email')})

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)
        
        return jsonify({'error': 'Invalid login credentials'}), 401

class Show:
    def show_attendance(self):
        atten_file = pd.read_csv('attendance.csv')
        return render_template('attendance.html', tables=[atten_file.to_html()], titles=['Attendance'])
    
    def download_atendance(self):
        with open ('attendance.csv', 'r') as f:
            csv = f.read()
        
        return csv

class DetectAttendance:

    def detectAttendance(self):
        path = r'./Samples'
        images = []
        className = []

        myList = os.listdir(path)
        print(myList)

        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            className.append(os.path.splitext(cl)[0])
        print(className)


        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                try:
                    encode = face_recognition.face_encodings(img)[0]
                except IndexError as e:
                    print(e)
                    exit(1)
                print(len(encode))
                encodeList.append(encode)
            return encodeList


        def markAttendance(name):
            with open('attendance.csv', 'w+') as f:
                myDataList = f.readlines()
                nameList = []
                for line in myDataList:
                    entry = line.split(',')
                    nameList.append(entry[0])
                if name not in nameList:
                    now = datetime.now()
                    dtString = now.strftime('%H:%M:%S')
                    f.writelines(f'\n{name}, {dtString}')


        encodeListKnown = findEncodings(images)
        print('Encoding Complete')

        img_path = r'./shots'
        dir_path = r'./shots'
        imageList = os.listdir(img_path)

        for images in imageList:
            count = 0
            new_path = img_path + '\\' + imageList[count]

            count += 1

            print(new_path)
            img = cv2.imread(new_path)

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDist = face_recognition.face_distance(encodeListKnown, encodeFace)
                print(faceDist)
                matchIndex = np.argmin(faceDist)

                if matches[matchIndex]:
                    name = className[matchIndex].upper()
                    print(name)
                    print("Detection complete")
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)
        # delete the files in the shots directory
        print('Program complete')
        # sleep for 2 secs
        time.sleep(2)

class RenderVideo(DetectAttendance):

    camera = cv2.VideoCapture(0)
    global capture, switch
    capture = 0
    switch = 1

    # make shots directory to save pics
    try:
        os.mkdir('./shots')
    except OSError as error:
        pass

    def gen_frames(self):  # generate frame by frame from camera

        global out, capture, rec_frame
        while True:
            success, frame = self.camera.read()
            if success:
                if capture:
                    capture = 0
                    now = datetime.now()
                    p = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":", ''))])
                    cv2.imwrite(p, frame)
                try:
                    ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except Exception as e:
                    pass

            else:
                pass
    
    def tasks(self):
        global switch, camera
        if request.method == 'POST':
            if request.form.get('click') == 'CAPTURE IMAGE':
                global capture
                capture = 1
                super().detectAttendance()
            elif request.form.get('stop') == 'START CAMERA':
                if switch == 1:
                    switch = 0
                    self.camera.release()
                    cv2.destroyAllWindows()
                else:
                    self.camera = cv2.VideoCapture(0)
                    switch = 1
        elif request.method == 'GET':
            return render_template('dashboard.html')
        return render_template('dashboard.html')