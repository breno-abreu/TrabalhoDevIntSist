import json
import requests
from pathlib import Path
import os.path
import pandas as pd
import numpy as np

from requests_toolbelt.multipart.encoder import MultipartEncoder


URL = "http://localhost:5000"

un = "breno"
pw = ""
token = ""

def main():
    """opt = 0
    print("Bem vindo!\n")
    while opt != "0":
        opt = input("\nDigite o número de uma das opções abaixo!\n" +
                "Cadastrar - 1\n" +
                "Login - 2\n" +
                "Testar token - 3\n" +
                "Sair - 0\n"
                ).strip()

        if opt == "1":
            username = input("Usuario: ")
            password = input("Senha: ")
            data = {'user' : str(username), 'pass' : str(password)}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            
            resp = requests.post(url = URL+'/cadastrar', data = json.dumps(data), headers=headers)
            
            #r = requests.post(url, data=json.dumps(data), headers=headers)
            if resp.ok:
                print("Cadastro feito com sucesso!")
            else:
                print("O cadastro não foi efetuado!")
        if opt == "2":
            username = input("Usuario: ")
            password = input("Senha: ")
            data = {'user' : str(username), 'pass' : str(password)}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            
            resp = requests.post(url = URL+'/login', data = json.dumps(data), headers=headers)
            
            #r = requests.post(url, data=json.dumps(data), headers=headers)
            if resp.ok:
                token = (resp.json())['token']
                print(token)
                print("Logado com sucesso!")
            elif resp.status_code == 406:
                print("Usuario/Senha incorreto!")
            else:
                print("Nao foi possivel efetuar o login!")

        if opt == "3":  
            #data = {'token' : str(token)}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            resp = requests.get(url = URL+'/ping'+'?token='+token, headers=headers) #, data = json.dumps(data), headers=headers)  
            print(resp.text)

        if opt == '0':
            print("Saindo...")"""
    
    send_signal()
    #list_images()
    #download_image()


def send_signal():
    resp = None
    while True:
        path = input("Informe o caminho do arquivo de sinal: ")
        path = './files/a-1.csv' #TEMP
        file = Path(path)
        extension = os.path.splitext(path)[1]
        if file.is_file() and extension == '.csv':
            break
        else:
            print("Arquivo não encontrado ou com extensão não suportada!")
    
    name = input("Informe o nome e a extensão do arquivo de imagem: ")
    name = 'g5.png' #TEMP

    while True:
        algorithm = input("Escolha o algoritmo utilizado\n[(1) - CGNE | (2) - FISTA]: ")
        algorithm = '1' #TEMP
        data = {'user' : un, 'name' : name}

        if algorithm != '1' and algorithm != '2':
            print("Opção não existente!")
        
        else:
            if algorithm == '1':
                data['algorithm'] = 'CGNE'
                
            elif algorithm == '2':
                data['algorithm'] = 'FISTA'

            vector = pd.read_csv(path, sep=';', header=None)
            vector = vector.replace(',', '.', regex=True)
            vector = vector.apply(pd.to_numeric, errors='coerce')
            vector = vector.to_numpy()

            data['signal'] = vector.tolist()
            resp = requests.post(url=URL + '/enviar_sinal', json=data)
            
            break
               
    if resp.ok:
        print("O Sinal foi enviado para o servidor")
    else:
        print("Falha ao enviar sinal para o servidor")


def list_images():
    payload = {'user' : un}
    resp = requests.get(url=URL + '/listar_imagens', params=payload)
    if resp.ok:
        img_list= resp.json()
        if len(img_list) > 0:
            for image in img_list:
                print("Usuário: " + image['username'] + "  Nome: " + image['name'])
        
        else:
            print("Nenhuma imagem encontrada")
        
    else:
        print("Não foi possível carregar a lista de imagens!")


def download_image():
    name = input("Qual imagem deseja baixar?: ")
    name = 'g1.png'
    payload = {'user' : un, 'name' : name}
    resp = requests.get(url=URL + '/baixar_imagem', params=payload, stream=True)
    if resp.ok:
        with open('img.png', 'wb') as file:
            for chunk in resp:
                file.write(chunk)
                
        print("Imagem salva")
    
    else:
        print("Não foi possível baixar a imagem")

if __name__ == '__main__':
    main()
