import json
from flask import Flask, request, jsonify, make_response, send_file
from config import app, db, Users, Images
from flask import Flask, jsonify, request, make_response
import pandas as pd
import numpy as np
import cv2 as cv
from numpy import linalg as la
from threading import Thread
from datetime import datetime
import jwt 
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


def run_cgne(data):
    """ Aplica o algoritmo CGNE em um sinal recebido """

    try:
        name = data['name']
        print(f"Iniciando algoritmo CGNE")

        img_path = '/images/' + name
        start_time = datetime.now()

        # Carrega a matriz de modelo
        matrix_path = "./files/H-1.csv"
        matrix = pd.read_csv(matrix_path, header=None)

        # Transforma os valores em valores numéricos e caso um deles
        # tenha um tipo diferente é registrado como NaN
        matrix = matrix.apply(pd.to_numeric, errors='coerce')
        matrix = matrix.to_numpy()

        # Inicializa as variáveis descritas no algoritmo
        r = np.array(data['signal'])
        p = np.dot(np.transpose(matrix), r)
        image = np.zeros(len(p))

        for i in range(30):
            print(f"[ITERAÇÃO {i + 1}]")
            # Linha 1 do algoritmo
            alpha = np.dot(np.transpose(r), r) / np.dot(np.transpose(p), p)

            # Linha 2 do algoritmo
            image = np.add(image, alpha * np.transpose(p))

            # Linha 3 do algoritmo
            r_aux = np.copy(r)
            r = r - alpha * np.dot(matrix, p)

            # Cálculo de erro. Quando o valor é atingido o algoritmo para.
            erro = la.norm(r, 2) - la.norm(r_aux, 2)
            if erro < 1e-4:
                break

            # Linha 4 do algoritmo
            beta = np.dot(np.transpose(r), r) / np.dot(np.transpose(r_aux), r_aux)

            #Linha 5 do algoritmo
            p = np.add(np.matmul(np.transpose(matrix), r), beta * p)

        # Encontra o valor absoluto do menor valor no vetor da imagem
        min_value = abs(image.min())

        # Encontra o maior valor no vetor da imagem e soma com o menor
        max_value = image.max() + min_value

        # Percorre o vetor da imagem alterando-o para que os valores finais
        # fiquem entre 0 e 255, assim podendo salvar a imagem em preto e branco
        for i in range(3600):
            image[0][i] = (image[0][i] + min_value) / max_value * 255
            #image[0][i] *= 255

        # Transforma o vetor em uma matriz de 60x60
        image = image.reshape((60, 60), order='F')

        # Amplia a imagem em 10 vezes
        res = cv.resize(image, (600, 600), interpolation = cv.INTER_NEAREST)

        # Salva a imagem
        cv.imwrite('.' + img_path, res)

        # Calcula a duração total do algoritmo
        finish_time = datetime.now()
        duration = (finish_time - start_time).total_seconds()
        duration = str(duration) + 's'

        # Cria um objeto contendo as informações da imagem
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

        # Salva as informações no banco de dados
        db.session.add(image)
        db.session.commit()

        print("Imagem salva")
    
    except Exception as e:
        print("Não foi possível gerar a imagem")
        print(e)


def run_fista(data):
    """ Executa o algoritmo FISTA no vetor recebido """
    try:
        name = data['name']
        vector = np.array(data['signal'])

        print(f"Iniciando algoritmo FISTA")

        img_path = '/images/' + name
        start_time = datetime.now()

        # Carrega a matriz de modelo
        path = "./files/H-1.csv"
        matrix = pd.read_csv(path, header=None)

        # Transforma os valores em valores numéricos e caso um deles
        # tenha um tipo diferente é registrado como NaN
        matrix = matrix.apply(pd.to_numeric, errors='coerce')
        matrix = matrix.to_numpy()

        # Inicializa as variáveis descritas no algoritmo
        image = np.zeros(3600)
        y = np.zeros(3600)
        alpha = 1

        for i in range(2):
            print("[ITERAÇÃO {0}]".format(i + 1))
            # Faz o cálculo do coeficiente de regularização
            lam = np.max(np.abs(np.dot(np.transpose(matrix), vector))) * 0.1

            # Faz o cálculo do fator de redução
            c = la.norm(np.matmul(np.transpose(matrix), matrix), ord=2)

            # Linha 1 do algoritmo
            image_old = np.copy(image)
            x = np.transpose(vector)[0] - np.dot(matrix, y)
            image = len(vector) * (lam / c) * (np.add(y, np.dot(1 / c * np.transpose(matrix), x)))

            # Linha 2 do algoritmo
            alpha_old = alpha
            alpha = (1 + np.sqrt(1 + 4 * alpha ** 2)) / 2

            # Linha 3 do algoritmo
            y = image + ((alpha_old - 1) / alpha) * (image - image_old)

        # Encontra o valor absoluto do menor valor no vetor da imagem
        min_value = abs(image.min())

        # Encontra o maior valor no vetor da imagem e soma com o menor
        max_value = image.max() + min_value

        # Percorre o vetor da imagem alterando-o para que os valores finais
        # fiquem entre 0 e 255, assim podendo salvar a imagem em preto e branco
        for i in range(3600):
            image[i] = (image[i] + min_value) / max_value * 255
            #image[i] *= 255

        # Transforma o vetor em uma matriz de 60x60
        image = image.reshape((60, 60), order='F')

        # Amplia a imagem em 10 vezes
        res = cv.resize(image, (600, 600), interpolation = cv.INTER_NEAREST)

        # Salva a imagem
        cv.imwrite('.' + img_path, res)

        # Calcula a duração total do algoritmo
        finish_time = datetime.now()
        duration = (finish_time - start_time).total_seconds()
        duration = str(duration) + 's'

        # Cria um objeto contendo as informações da imagem
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

        # Salva as informações no banco de dados
        db.session.add(image)
        db.session.commit()

        print("Imagem salva")
    
    except Exception as e:
        print("Não foi possível gerar a imagem")
        print(e)
    

@app.route('/enviar_sinal', methods=['POST'])
@token_required
def get_signal():
    """ Recebe o sinal enviado pelo cliente e executa um dos algoritmos 
        criando uma nova thread para a execução do algoritmo escolhido """

    data = request.json

    if data['algorithm'] == 'FISTA':
        thread = Thread(target=run_fista, args=(data,))
        thread.start()

    elif data['algorithm'] == 'CGNE':
        thread = Thread(target=run_cgne, args=(data,))
        thread.start()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route('/listar_imagens', methods=['GET'])
@token_required
def get_image_list():
    """ Envia a lista de imagens pertencentes ao usuário informado nos parâmetros recebidos """

    username = request.args.get('user')

    # Procura por todas as imagens de um determinado usuário
    image_list_db = Images.query.filter_by(username=username).all()
    image_list = []
    for image in image_list_db:
        image_list.append(image.asdict())

    # Envia a lista contendo as informações das imagens em formato json
    return jsonify(image_list)


@app.route('/baixar_imagem', methods=['GET'])
@token_required
def download_image():
    """ Envia a imagem requisitada pelo usuário """

    username = request.args.get('user')
    img_name = request.args.get('name')

    # Procura no banco de dados o registro da imagem requerida 
    image = Images.query.filter_by(username=username, name=img_name).first()
    if image != None:
        # Envia a imagem para o cliente
        return send_file('.' + image.path, mimetype='image/png')
    else:
        print("Imagem não encontrada")
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'}


def get_account(user):
    return Users.query.filter_by(username=user).first()


def verifica_login(data):
    account = get_account(data['user'])
    print(data['pass'])
    print(account.password)
    if account and account.password ==  data['pass']:
        return account
    return None


@app.route('/ping', methods=['GET'])
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

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})


if __name__ == "__main__":
    """ Executa o servidor """
    app.run(debug=True,threaded=True)


# TODO : medir cpu e memoria enquanto os algortmos rodam
# gives a single float value
#psutil.cpu_percent()
# gives an object with many fields
#psutil.virtual_memory()