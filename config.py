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
    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(15), nullable=False)
    images = db.relationship('Images', backref='user', lazy=True)

    def __repr__(self):
        return f"Username: {self.username}, Password: {self.password}"

    def asdict(self):
        return {'username' : self.username, 
                'password' : self.password}

class Images(db.Model):
    img_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)
    path = db.Column(db.String(100))
    name = db.Column(db.String(25))
    algorithm = db.Column(db.String(10))
    start_time = db.Column(db.DateTime)
    finish_time = db.Column(db.DateTime)
    size = db.Column(db.String(15))
    n_iterations = db.Column(db.Integer)
    duration = db.Column(db.String(20))
    status = db.Column(db.String(10))

    def __repr__(self):
        return f"{self.username}, {self.name}, {self.path}, {self.algorithm}, {self.start_time}, {self.finish_time}, {self.duration}"
    
    def asdict(self):
        return {'username' : self.username, 
                'name' : self.name,
                'algorithm' : self.algorithm,
                'start_time' : self.start_time,
                'finish_time' : self.finish_time,
                'duration' : self.duration,
                'n_iterations' : self.n_iterations,
                'size' : self.size}