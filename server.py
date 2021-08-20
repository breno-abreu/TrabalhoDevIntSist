#pip install flask-mysqldb
from operator import truediv
import time
import json
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask.wrappers import Response
from sqlalchemy.orm import defaultload
from config import app, db, Users, session, Images
#import psutil
import sys, os
import pathlib
from flask import Flask, jsonify, request, make_response


@app.route('/enviar_sinal', methods=['POST'])
def get_signal():
    aux = json.loads(request.form['data'])
    csv = request.files['signal']
    #file.save(os.path.join('./files_test/' + file.filename))

    vetor = pd.read_csv(path, sep=';', header=None)
    vetor = vetor.replace(',', '.', regex=True)
    vetor = vetor.apply(pd.to_numeric, errors='coerce')

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 







































"""import jwt 
import datetime
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #http://127.0.0.1:5000/route?token=alshfjfjdklsfj89549834ur
        print("TENTANDO COM O TOKEN: " + token)
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

def get_account(user):
    return Users.query.filter_by(username=user).first()

def verifica_login(data):

    account = get_account(data['user'])
    print(data['pass'])
    print(account.password)
    if account and account.password ==  data['pass']:
        return account
    return None

@app.route('/ping', methods=['get'])
@token_required
def ping():
    return jsonify({'message' : 'Seu token é valido!.'})

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    data = request.json
    
    account = get_account(data['user'])
    if not account:
        user = Users(data['user'], data['pass'])
        db.session.add(user)
        if db.session:
            db.session.commit()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    
    return json.dumps({'success':False}), 406, {'ContentType':'application/json'}


@app.route('/login', methods=['POST'])
def login():
    
    account = verifica_login(request.json)
    if account:
        token = jwt.encode({'user' : account.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=50)}, app.config['SECRET_KEY'],  algorithm="HS256")
        return jsonify({'token' : token}) #.decode('UTF-8')

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})"""

# TODO : medir cpu e memoria enquanto os algortmos rodam
# gives a single float value
#psutil.cpu_percent()
# gives an object with many fields
#psutil.virtual_memory()

if __name__ == "__main__":
    """ Executa o servidor """
    app.run(debug=True,threaded=True)