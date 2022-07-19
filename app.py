from flask import Flask, render_template, request, redirect, Response, url_for, flash, jsonify, session
from functools import wraps
from user.models import User, RenderVideo, Show
import pymongo

# create the flask app
app = Flask(__name__, template_folder='templates')
# app secret key
app.secret_key = b'\x9e\x87\xfd\x1dK\xbb\xed\xa2\x12q}D\xd8\xdc\x92\xec'

# connect to mongodb
client = pymongo.MongoClient('localhost', 27017)
db = client.user_login

# decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap


# Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/user/signup', methods=['GET', 'POST'])
def signup_page():
    return render_template('signup.html')

@app.route('/user/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')

@app.route('/user/signout')
def signout():
    return User().signout()

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(RenderVideo().gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests', methods=['GET', 'POST'])
@login_required
def requests():
    return RenderVideo().tasks()

@app.route('/show-attendance', methods=['GET', 'POST'])
@login_required
def show_attendance():
    return Show().show_attendance()

@app.route('/download-attendance')
@login_required
def get_csv():
    return Response(Show().download_atendance(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=attendance.csv'})


@app.route('/user/login/validate', methods=['POST'])
def login_validate():
    return User().login(db)

@app.route('/user/signup/validate', methods=['POST'])
def signup_validate():
    return User().signup(db)

if __name__ == '__main__':
    app.run(debug=True)