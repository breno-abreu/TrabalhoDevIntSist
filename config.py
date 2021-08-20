import pathlib
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

curr_path = str(pathlib.Path(__file__).parent.resolve())
curr_path = curr_path.replace("\\","/")
DB_PATH = 'sqlite:///'+ curr_path +  '/data/database.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SECRET_KEY'] = 'segredo'

db = SQLAlchemy(app)

class Users(db.Model):
    username = db.Column(db.String(30), primary_key = True)
    password = db.Column(db.String(15), nullable=False)
    images = db.relationship('Images', backref='user', lazy=True)

class Images(db.Model):
    img_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)
    path = db.Column(db.String(100))
    algorithm = db.Column(db.String(10))
    start_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)
    size = db.Column(db.String(15))
    n_iterations = db.Column(db.Integer)
    duration = db.Column(db.Interval)
    status = db.Column(db.String(10))