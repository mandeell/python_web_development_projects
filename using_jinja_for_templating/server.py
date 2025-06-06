from flask import Flask, render_template, request
import random
from datetime import datetime
import requests


app = Flask(__name__)

@app.route('/')
def home():
    random_number = random.randint(1, 10)
    current_year = datetime.now().year
    return render_template('index.html', random_number=random_number, year=current_year)

app.route('/guess/<<some_name>>')
def guess(some_name):
    name = some_name
    response = requests.get()

    return render_template('guess.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)