import json
import requests
from pathlib import Path
import os.path
import pandas as pd
import numpy as np


URL = "http://localhost:5000"

un = "breno"
pw = ""
token = ""

def main():
    """ Apresenta um menu de opções para o usuário """

    opt = 0
    print("Bem vindo!\n")
    while opt != "0":
        opt = input("\nDigite o número de uma das opções abaixo!\n" +
                    "Cadastrar - 1\n" +
                    "Login - 2\n" +
                    "Testar token - 3\n" +
                    "Enviar sinal - 4\n" + 
                    "Listar imagens - 5\n" +
                    "Baixar imagem - 6\n" +
                    "Sair - 0\n"
                    ).strip()

        if opt == "1":
            # Cadastra um usuário no servidor
            register_user()
            
        elif opt == "2":
            # Faz o login de um usuário
            user_login()

        elif opt == "3":  
            # Testa o tolken do usuário
            test_tolken()
        
        elif opt == "4":
            # Envia um sinal para o servidor
            send_signal()
        
        elif opt == "5":
            # Recebe uma lista de imagens e suas informações
            list_images()

        elif opt == "6":
            # Baixa uma imagem do servidor
            download_image()

        elif opt == '0':
            print("Saindo...")
        
        else:
            print("Opção não existente!")
    

def register_user():
    """ Faz o cadastro de um usuário no servidor """

    username = input("Usuario: ")
    password = input("Senha: ")
    data = {'user' : str(username), 'pass' : str(password)}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    resp = requests.post(url = URL+'/cadastrar', data = json.dumps(data), headers=headers)
    
    if resp.ok:
        print("Cadastro feito com sucesso!")
    else:
        print("O cadastro não foi efetuado!")


def user_login():
    """ Faz o login de um usuário """

    username = input("Usuario: ")
    password = input("Senha: ")
    data = {'user' : str(username), 'pass' : str(password)}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    
    resp = requests.post(url = URL+'/login', data = json.dumps(data), headers=headers)
    
    if resp.ok:
        token = (resp.json())['token']
        print(token)
        print("Logado com sucesso!")
    elif resp.status_code == 406:
        print("Usuario/Senha incorreto!")
    else:
        print("Nao foi possivel efetuar o login!")


def test_tolken():
    """ Testa o tolken de um usuário """

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    resp = requests.get(url = URL+'/ping'+'?token='+token, headers=headers)
    print(resp.text)


def send_signal():
    """ Carrega um sinal de um arquivo .csv, faz o cálculo de ganho de sinal
        e envia-o para o servidor juntamente com outras informações """

    resp = None

    while True:
        path = input("Informe o caminho do arquivo de sinal: ")
        path = './files/g-1.csv' #TEMP
        file = Path(path)
        extension = os.path.splitext(path)[1]

        # Verifica se o arquivo existe e se a extensão é .csv
        if file.is_file() and extension == '.csv':
            break
        else:
            print("Arquivo não encontrado ou com extensão não suportada!")
    
    name = input("Informe o nome e a extensão do arquivo de imagem que será salva no servidor: ")
    name = 'g5.png' #TEMP

    while True:
        algorithm = input("Escolha o algoritmo utilizado\n[(1) - CGNE | (2) - FISTA]: ")
        algorithm = '1' #TEMP

        # Cria o dicionário que será enviado como json para o servidor contendo
        # o nome do usuário e o nome do arquivo de imagem que será gerado no servidor
        data = {'user' : un, 'name' : name}

        if algorithm != '1' and algorithm != '2':
            print("Opção não existente!")
        
        else:
            if algorithm == '1':
                data['algorithm'] = 'CGNE'
                
            elif algorithm == '2':
                data['algorithm'] = 'FISTA'

            # Carrega um arquivo .csv local
            vector = load_csv_file(path)

            # Realiza o calculo de ganho de sinal
            vector = calculate_signal_gain(vector)

            # Inseri osinal no dicionário
            data['signal'] = vector.tolist()

            # Envia um post para o servidor contendo o dicionário gerado
            # e recebe a resposta
            resp = requests.post(url=URL + '/enviar_sinal' +'?token='+token, json=data)
            break
               
    if resp.ok:
        print("O Sinal foi enviado para o servidor")
    else:
        print("Falha ao enviar sinal para o servidor")


def list_images():
    """ Faz o requerimento da lista de arquivos de imagem presentes no servidor
        de um determinado usuário """

    # Cria um dicionário contendo o parâmetro que será enviado
    payload = {'user' : un}

    # Envia um get para o servidor enviando o nome do usuário como parâmetro
    # e recebe a resposta
    resp = requests.get(url=URL + '/listar_imagens' +'?token='+token, params=payload)

    if resp.ok:
        # Recebe um json contendo as informações das imagens
        img_list= resp.json()

        # imprime as informações de todas as imagens
        if len(img_list) > 0:
            for image in img_list:
                print("Usuário: " + image['username'] + "  Nome: " + image['name'])
        
        else:
            print("Nenhuma imagem encontrada")
        
    else:
        print("Não foi possível carregar a lista de imagens!")


def download_image():
    """ Baixa uma imagem presente no servidor """

    name = input("Qual imagem deseja baixar?: ")
    name = 'g1.png' # TEMP

    # Cria um dicionário contendo os parâmetros da requisição
    payload = {'user' : un, 'name' : name}

    # Envia um get para o servidor juntamente tendo o dicionário como parâmetros
    # e recebe a resposta
    resp = requests.get(url=URL + '/baixar_imagem' +'?token='+token, params=payload, stream=True)
    if resp.ok:
        path = input("Especifique o caminho e o nome do arquivo que será salvo: ")
        # Salva a imagem recebida na resposta
        with open(path, 'wb') as file:
            for chunk in resp:
                file.write(chunk)

        print("Imagem salva")
    
    else:
        print("Não foi possível baixar a imagem")


def calculate_signal_gain(vector):
    """ Faz o cálculo de ganho de sinal de um vetor """

    # Transforma o vetor em uma matriz retangular
    vector = vector.reshape((794, 64))

    # Para cada coluna realiza o algoritmo de cálculo de ganho de sinal
    for i in range(64):
        for j in range(794):
            gamma = 100 + 1 / 20 * j * np.sqrt(j)
            vector[j][i] *= gamma 
    
    # Transforma a matriz em um vetor com as mesmas dimensões do vetor recebido
    return vector.reshape((50816, 1))


def load_csv_file(path):
    """ Carrega um arquivo .cvs utilziando a bilioteca Pandas e o 
        transforma em um vetor do NumPy """

    # Carrega o vetor 
    vector = pd.read_csv(path, sep=';', header=None)

    # Substitui as vírgulas por pontos
    vector = vector.replace(',', '.', regex=True)

    # Transforma os valores em valores numéricos e caso um deles
    # tenha um tipo diferente é registrado como NaN
    vector = vector.apply(pd.to_numeric, errors='coerce')

    # Retorna o vetor transformado em vetor do NumPy
    return vector.to_numpy()

if __name__ == '__main__':
    main()
