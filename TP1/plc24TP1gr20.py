from flask import Flask, render_template
import re
import json

app = Flask(__name__)

@app.route('/')
def index1():
    return render_template("main.html")

@app.route('/index')
def index():
    # Variáveis para guardar o atleta mais novo e mais velho respetivamente
    menor = float('inf')
    maior = float('-inf')

    # Variáveis para contar o número de atletas masculinos e femininos
    masculino = 0
    feminino = 0

    # Dicionário que vai agrupar os desportos praticados num determinado ano
    lista_anos = {}

    # Dicionário para guardar o nº de atletas aptos a competir em cada ano
    lista_aptos = {}

    # Dicionário que vai guardar a média de aptos e não aptos por ano em percentagem
    media = {}

    # Lista onde vão ser guardadas as sugestões de nomes a trocar, juntamente com a sua normalização
    sugestao_nomes = []

    # Objetivo da alínea c) ii) 
    # Função auxiliar que vai contar o número de atletas por cada desporto
    def conta_desportos(lista_anos):
        modalidade_total = {}
        for ano in lista_anos:
            for desporto, total in lista_anos[ano].items():
                modalidade_total[desporto] = modalidade_total.get(desporto, 0) + total
        return modalidade_total

    try:
        with open("emd.csv", 'r') as df:
            content = df.read()
            res = re.split(r"\n", content)
            res.pop(0)

            for linha in res:
                info = re.split(r",", linha)

                # Objetivo da alínea a) Calcular as Idades extremas dos registos 
                menor = min(int(info[5]), menor)
                maior = max(int(info[5]), maior)

                    #  Objetivo da alínea b) Calcular a distribuição por Género no total
                if info[6] == "M":
                    masculino += 1
                elif info[6] == "F":
                    feminino += 1
                    
                #  Objetivo da alínea c) i) Calcular a distribuição por Modalidade em cada ano
                ano = re.match(r'[0-9]{4}', info[2])
                if ano:
                    ano = ano.group(0)
                    desporto = info[8]
                    
                    if ano not in lista_anos:
                        lista_anos[ano] = {}
                    if desporto not in lista_anos[ano]:
                        lista_anos[ano][desporto] = 0
                    
                    lista_anos[ano][desporto] += 1

                # Objetivo da alínea d) Calcular a pertentagem de atletas aptos e não aptos por cada ano
                apto = info[12]
                if ano not in lista_aptos:
                    lista_aptos[ano] = {0: 0, 1: 0}
                if apto == "true":
                    lista_aptos[ano][0] += 1
                lista_aptos[ano][1] += 1     

                if info[6] != "F":
                    sugestao_nomes.append(f">> Sugestao: Alterar o nome do atleta com o Id {info[0]}, {info[3]} {info[4]} --> {info[4]} {info[3]}")

        # Organizar lista_anos e calcular percentagens
        lista_anos = dict(sorted(lista_anos.items()))
        for ano in lista_anos:
            lista_anos[ano] = dict(sorted(lista_anos[ano].items(), key=lambda t: t[0]))
            media[ano] = round(lista_aptos[ano][0] * 100 / lista_aptos[ano][1], 2)

        with open('mensagem.json', 'w') as json_file:
            json.dump(sugestao_nomes, json_file, indent=4)

    except FileNotFoundError:
        print("O arquivo emd.csv não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    conta_numeros = conta_desportos(lista_anos)

    # Esta função vai registar o código html para depois registar todos os resultados no ficheiro index.html
    def gerar_html(menor, maior, masculino, feminino, lista_anos, conta_numeros, media):  

        html = "<html>\n<head></head>\n<body>\n"
        
        # Adicionar um título
        html += "<h2>Valores finais</h2>\n"

        # Adicionar parágrafos com as idades
        html += f"<p>Menor Idade: {menor} anos</p>\n"
        html += f"<p>Maior Idade: {maior} anos</p>\n"
        html += "<br>\n"
        html += f"<p>Masculinos: {masculino}</p>\n"
        html += f"<p>Femininos: {feminino}</p>\n"
        html += "<br>\n"
        html += "<h2>Modalidades por Ano:</h2>\n"
        html += "<table>\n"
        html += "<thead>\n"
        html += "<tr>\n"
        html += "<th>Ano</th>\n"
        html += "<th>Modalidade</th>\n"
        html += "<th>Total</th>\n"
        html += "</tr>\n"
        html += "</thead>\n"
        html += "<tbody>\n"

        for ano, modalidades in lista_anos.items():
            for modalidade, total in modalidades.items():
                html += "<tr>\n"
                html += f"<td>{ano}</td>\n"
                html += f"<td>{modalidade}</td>\n"
                html += f"<td>{total}</td>\n"
                html += "</tr>\n"

        html += "</tbody>\n"
        html += "</table>\n"
        html += "<br>\n"
        html += "<h2>Total de Praticantes por Modalidade:</h2>\n"
        html += "<table>\n"
        html += "<thead>\n"
        html += "<tr>\n"
        html += "<th>Modalidade</th>\n"
        html += "<th>Total</th>\n"
        html += "</tr>\n"
        html += "</thead>\n"
        html += "<tbody>\n"

        for modalidade, total in conta_numeros.items():
            html += "<tr>\n"
            html += f"<td>{modalidade}</td>\n"
            html += f"<td>{total}</td>\n"
            html += "</tr>\n"

        html += "</tbody>\n"
        html += "</table>\n"
        html += "<br>\n"
        html += "<h2>Percentagem de Aprovação anual:</h2>\n"
        html += "<table>\n"
        html += "<thead>\n"
        html += "<tr>\n"
        html += "<th>Ano</th>\n"
        html += "<th>Percentagem Aptos</th>\n"
        html += "<th>Percentagem não Aptos</th>\n"
        html += "</tr>\n"
        html += "</thead>\n"
        html += "<tbody>\n"

        for ano, percentagem in media.items():
            html += "<tr>\n"
            html += f"<td>{ano}</td>\n"
            html += f"<td>{percentagem}</td>\n"
            html += f"<td>{100 - percentagem}</td>\n"
            html += "</tr>\n"

        html += "</tbody>\n"
        html += "</table>\n"
        html += "</body>\n</html>"

        return html

    html= gerar_html(menor, maior, masculino, feminino, lista_anos, conta_numeros, media)

    # Escrever a string HTML no ficheiro idades.html
    with open("index.html", "w") as file:
        file.write(html)

    return render_template("main2.html", menor=menor, maior=maior, masculino=masculino, feminino=feminino, lista_anos=lista_anos, conta_numeros=conta_desportos(lista_anos), media=media)

if __name__ == '__main__':
    app.run(debug=True)