#pip install flask-mysqldb
from operator import truediv
import time
import json
from flask import Flask, request, jsonify, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask.wrappers import Response
from sqlalchemy.orm import defaultload
from config import app, db, Users, session, Images
#import psutil
import sys, os
import pathlib
from flask import Flask, jsonify, request, make_response
import pandas as pd
import numpy as np
import cv2 as cv
from numpy import linalg as la
from threading import Thread
from datetime import datetime

def run_cgne(data):
    name = data['name']
    vector = np.array(data['signal'])

    print(f"Iniciando algoritmo CGNE para o sinal {name}")

    img_path = '/images/' + data['name']
    start_time = datetime.now()

    path = "./files/H-1.csv"
    matrix = pd.read_csv(path, header=None)
    matrix = matrix.apply(pd.to_numeric, errors='coerce')
    matrix = matrix.to_numpy()

    r = vector
    p = np.dot(np.transpose(matrix), r)
    image = np.zeros(len(p))
    i = 0

    for i in range(40):
        print(f"[ITERAÇÃO {i}]")
        # linha 1
        alpha = np.dot(np.transpose(r), r) / np.dot(np.transpose(p), p)

        # linha 2
        image = np.add(image, alpha * np.transpose(p))

        # linha 3
        r_aux = np.copy(r)
        r = r - (alpha * np.dot(matrix, p))

        # linha 4
        beta = np.dot(np.transpose(r), r) / np.dot(np.transpose(r_aux), r_aux)

        #linha 5
        p = np.add(np.dot(np.transpose(matrix), r), beta * p)

        # calculo de erro
        erro = np.sqrt(np.dot(np.transpose(r), r))
        if erro < 1e-4:
            break

    menor = abs(image.min())
    maior = image.max() + menor

    for i in range(3600):
        #image[0][i] = (image[0][i] + menor) / maior * 255
        image[0][i] *= 255

    image = image.reshape((60, 60), order='F')
    res = cv.resize(image, (600, 600), interpolation = cv.INTER_NEAREST)
    cv.imwrite('.' + img_path, res)

    finish_time = datetime.now()
    duration = (finish_time - start_time).total_seconds()
    duration = str(duration) + 's'

    image = Images(username=data['user'], 
                   name=data['name'], 
                   algorithm=data['algorithm'],
                   path=img_path,
                   size='600x600',
                   n_iterations=2,
                   status='Concluído',
                   start_time=start_time,
                   finish_time=finish_time,
                   duration=duration)

    db.session.add(image)
    db.session.commit()

    print("Imagem salva")
    print(Images.query.all())


def run_fista(data):
    name = data['name']
    vector = np.array(data['signal'])

    print(f"Iniciando algoritmo FISTA para o sinal {name}")

    img_path = '/images/' + data['name']
    start_time = datetime.now()

    path = "./files/H-1.csv"
    matrix = pd.read_csv(path, header=None)
    matrix = matrix.apply(pd.to_numeric, errors='coerce')
    matrix = matrix.to_numpy()

    image = np.zeros(3600)
    y = np.zeros(3600)
    alpha = 1

    for i in range(2):
        print("[ITERAÇÃO {0}]".format(i + 1))
        # coeficiente de regularização
        lam = np.max(np.abs(np.dot(np.transpose(matrix), vector))) * 0.1

        # fator de redução
        c = la.norm(np.matmul(np.transpose(matrix), matrix), ord=2)

        # linha 1
        image_old = np.copy(image)
        x = np.transpose(vector)[0] - np.dot(matrix, y)
        image = len(vector) * (lam / c) * (np.add(y, np.dot(1 / c * np.transpose(matrix), x)))

        # linha 2
        alpha_old = alpha
        alpha = (1 + np.sqrt(1 + 4 * alpha ** 2)) / 2

        # linha 3
        y = image + ((alpha_old - 1) / alpha) * (image - image_old)


    menor = abs(image.min())
    maior = image.max() + menor

    for i in range(3600):
        image[i] = (image[i] + menor) / maior * 255
        #image[i] *= 255

    image = image.reshape((60, 60), order='F')
    res = cv.resize(image, (600, 600), interpolation = cv.INTER_NEAREST)
    cv.imwrite('.' + img_path, res)

    finish_time = datetime.now()
    duration = (finish_time - start_time).total_seconds()
    duration = str(duration) + 's'

    image = Images(username=data['user'], 
                   name=data['name'], 
                   algorithm=data['algorithm'],
                   path=img_path,
                   size='600x600',
                   n_iterations=2,
                   status='Concluído',
                   start_time=start_time,
                   finish_time=finish_time,
                   duration=duration)

    db.session.add(image)
    db.session.commit()

    print("Imagem salva")
    print(Images.query.all())
    

@app.route('/enviar_sinal', methods=['POST'])
def get_signal():
    data = request.json

    if data['algorithm'] == 'FISTA':
        thread = Thread(target=run_fista, args=(data,))
        thread.start()

    elif data['algorithm'] == 'CGNE':
        thread = Thread(target=run_cgne, args=(data,))
        thread.start()
    
    """image = Users(username='breno', password='123')

    db.session.add(image)
    db.session.commit()"""

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route('/listar_imagens', methods=['GET'])
def get_image_list():
    username = request.args.get('user')
    image_list_db = Images.query.filter_by(username=username).all()
    image_list = []
    for image in image_list_db:
        image_list.append(image.asdict())

    return jsonify(image_list)


@app.route('/baixar_image', methods=['GET'])
def download_image():
    username = request.args.get('user')
    img_name = request.args.get('name')
    image = Images.query.filter_by(username=username, name=img_name).first()
    if image != None:
        return send_file('.' + image.path, mimetype='image/png')
    else:
        print("image não encontrada")
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'}



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