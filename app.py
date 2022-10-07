from flask import Flask, request, render_template, session, redirect
import numpy as np
import pandas as pd
from synt_generator import DatasetGenerator

app = Flask(__name__)
dg = DatasetGenerator(row_count=100, numerical=[(1, 100,2)], categorical=[(['a','b','c'], 2)], word=[[5,1]], sentence=[[5,1]])


@app.route('/', methods=("POST", "GET"))
def html_table():
    df = dg()
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)


if __name__ == '__main__':
    app.run()