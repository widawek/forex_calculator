import requests
import pandas as pd
from flask import Flask, redirect, render_template, request


UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    return redirect("tabela")


@app.route("/tabela/")
def tabela():
    title = 'Tabela kursów walut w stosunku do złotówki'
    response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    data = response.json()
    df = pd.DataFrame(data[0]['rates'])
    df.to_csv('uploads/rates.csv', sep=';', index=False)
    df = df.rename(columns={'currency': 'Waluta', 'code': 'Kod',
                            'bid': 'Sprzedaż', 'ask': 'Kupno'})
    data = df.to_dict(orient='records')
    return render_template("table.html", main_title='tabela',
                           title=title, data=data)


@app.route("/calculator/", methods=['GET', 'POST'])
def calculator():
    title = 'Kalkulator walut'
    try:
        df = pd.read_csv('uploads/rates.csv', sep=";")
    except FileNotFoundError:
        return redirect("../tabela")

    options = df['currency'].tolist()
    ask = df['ask'].astype(float).to_list()

    # Logika dla POST (gdy formularz jest wysyłany)
    result = None
    if request.method == 'POST':
        selected_option = request.form.get('selected_option')
        multiplier = float(request.form.get('multiplier', 1))
        index_ = options.index(selected_option)
        result = round(ask[index_] * multiplier, 2)
        result = f"Za {multiplier} {selected_option} zapłacisz {result} złotych"

    return render_template("calculator.html", main_title='kalkulator',
                           title=title, options=options, result=result)


if __name__ == "__main__":
    app.run(debug=True)
