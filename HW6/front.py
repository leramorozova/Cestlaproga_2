import back
from flask import Flask
from flask import url_for, render_template, request, redirect

app = Flask(__name__)

# Главная страница
@app.route('/')
def form():
    return render_template('form.html')

# Результат перевода слова на дореволюционный
@app.route('/result')
def result():
    sent = request.args['word']
    translation = back.compiling(sent)
    return render_template('result.html', translation=translation)


if __name__ == '__main__':
    app.run(debug=True)