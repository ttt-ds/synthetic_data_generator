from flask import Flask, request, render_template, session, redirect
import numpy as np
import pandas as pd
from synt_generator import DatasetGenerator
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os


app = Flask(__name__)
dg = DatasetGenerator(row_count=100, numerical=[(1, 100,2)], categorical=[(['a','b','c'], 2)], word=[[5,1]], sentence=[[5,1]],datetime=[('2020-02-08 01:00 pm', '2022-01-01 01:00 pm')])
Bootstrap(app)

@app.route('/', methods=("POST", "GET"))
def html_table():
    df = dg()
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)


@app.route('/create/', methods=['post', 'get'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')  # запрос к данным формы
        password = request.form.get('password')

        if username == 'root' and password == 'pass':
            message = "Correct username and password"
        else:
            message = "Wrong username or password"

    return render_template('login.html', message=message)


@app.route("/getPlotCSV")
def getPlotCSV():
    with open("uploads/tmp.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=myplot.csv"})

@app.route('/table', methods=['post', 'get'])
def table():
    df = pd.DataFrame()
    if request.method == 'POST':
        rows_count = int(request.form.get('rows_count'))
        num_min = int(request.form.get('num_min'))
        num_max = int(request.form.get('num_max'))
        num_count = int(request.form.get('num_count'))

        dg = DatasetGenerator(row_count=rows_count, numerical=[(num_min, num_max, num_count)])

        df = dg()
        filepath = os.path.join('uploads', 'tmp.csv')
        df.to_csv(filepath)
        send_from_directory('uploads', 'tmp.csv', as_attachment=True)

    return render_template('table.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)

if __name__ == '__main__':
    app.run()