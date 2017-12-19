import HW_add_content
from flask import Flask
from flask import url_for, render_template, request, redirect

app = Flask(__name__)

# Главная страница с погодой и поиском. Еще там будет ссылка на sports.ru, но пока только красивый баннер

@app.route('/')
def form():
    temperature=HW_add_content.weather()
    if request.args:
        return render_template('result.html')
    return render_template('form.html', temperature=temperature)


@app.route('/result')
def result():
    word = request.args['word']
    translation = HW_add_content.main_translator(word)
    return render_template('result.html', translation=translation)


@app.route('/revolutionary')
def test():
    with open('translated.txt', 'r', encoding='UTF-8') as file:
        translated = file.read()
    return render_template('rev.html', translated = translated)


if __name__ == '__main__':
    app.run(debug=True)
