from flask import Flask, render_template
from synt_generator import DatasetGenerator
app = Flask(__name__)
generator = DatasetGenerator(row_count=10,numerical=[(1, 100,2)], categorical=[(['a','b','c'], 2)], word=[[5,1]], sentence=[[5,1]])

@app.route('/')
@app.route('/index')
def index():
    a = generator()
    return render_template("index.html", data=a)

if __name__ == '__main__':
    app.run()