from flask import Flask, render_template
import re
import json

app = Flask(__name__)

@app.route('/')
def index1():
    return render_template('main.html')

@app.route('/index')
def index():
    menor = float('inf')
    maior = float('-inf')
    masculino = 0
    feminino = 0
    lista_anos = {}
    lista_aptos = {}
    media = {}
    media2 = {}
    fim = []

    def conta_numeros(lista_anos):
        modalidade_total = {}
        for ano in lista_anos:
            for desporto, total in lista_anos[ano].items():
                if desporto not in modalidade_total:
                    modalidade_total[desporto] = 0
                modalidade_total[desporto] += total
        return modalidade_total

    with open("emd.txt", 'r') as df:
        content = df.read()
        res = re.split(r"\n", content)
        res.pop(0)
        for linha in res:
            final = re.split(r",", linha)

            menor = min(int(final[5]), menor)
            maior = max(int(final[5]), maior)

            if final[6] == "M":
                masculino += 1
            elif final[6] == "F":
                feminino += 1
            
            ano = re.match(r'[0-9]{4}', final[2])
            ano = ano.group(0)
            desporto = final[8]
            apto = final[12]

            if ano not in lista_anos:
                lista_anos[ano] = {}
            if desporto not in lista_anos[ano]:
                lista_anos[ano][desporto] = 0
            
            lista_anos[ano][desporto] += 1

            if ano not in lista_aptos:
                lista_aptos[ano] = {0: 0, 1: 0}
            if apto == "true":
                lista_aptos[ano][0] += 1
            lista_aptos[ano][1] += 1    
            
            pattern = f"{final[3]} {final[4]}"  

            if final[6] != "F":
                res = re.search(r"([a-z]+).([a-z]+)", final[10])
                if final[3].lower() != res.group(1) or final[4].lower() != res.group(2):
                    fim.append(pattern)
        
        for ano in lista_anos.keys():
            lista_anos = dict(sorted(lista_anos.items(), key=lambda t: t[0]))
            lista_anos[ano] = dict(sorted(lista_anos[ano].items(), key=lambda t: t[0]))
            media[ano] = round(lista_aptos[ano][0] * 100 / lista_aptos[ano][1], 2)
            media2[ano] = round((lista_aptos[ano][1] - lista_aptos[ano][0]) * 100 / lista_aptos[ano][1], 2)
            media = dict(sorted(media.items(), key=lambda t: t[0]))
            media2 = dict(sorted(media2.items(), key=lambda t: t[0]))
        with open('mensagem.json', 'w') as json_file:
            json.dump(fim, json_file, indent=4)

    return render_template('index.html', menor=menor, maior=maior, masculino=masculino, feminino=feminino, lista_anos=lista_anos, conta_numeros=conta_numeros(lista_anos), media=media, media2=media2)

if __name__ == '__main__':
    app.run(debug=True)
