import HW_add_content
from flask import Flask
from flask import url_for, render_template, request, redirect

app = Flask(__name__)

# Главная страница с погодой и поиском. Еще там ccылка на sports.ru.
@app.route('/')
def form():
    temperature = HW_add_content.weather()
    if request.args:
        return render_template('result.html')
    return render_template('form.html', temperature = temperature)

# Результат перевода слова на дореволюционный
@app.route('/result')
def result():
    word = request.args['word']
    translation = HW_add_content.main_translator(word)
    return render_template('result.html', translation = translation)

# Переведенный текст страницы и топ слов
@app.route('/revolutionary')
def rev():
    top = HW_add_content.top(HW_add_content.main_page())
    with open('translated.txt', 'r', encoding = 'UTF-8') as file:
        translated = file.read()
        print(translated)
    return render_template('rev.html', translated = translated, top = top)

# Тест на наличие яти
@app.route('/test')
def test():
    choice = HW_add_content.yat_test()
    if request.args:
        return render_template('test_res.html')
    return render_template('test.html', choice = choice)

# Ответ на тест
@app.route('/test_res')
def test_res():
    user_answer = request.args['answer']
    with open('answer.txt', 'r', encoding = 'UTF-8') as file:
        answer = file.read()
    if 'ѣ' in answer and user_answer == 'yat':
        reaction = 'Вы правы!'
    elif 'ѣ' not in answer and user_answer == 'no_yat':
        reaction = 'Вы правы!'
    else:
        reaction = 'А вот и нет!'
    return render_template('test_res.html', reaction = reaction, answer = answer)


if __name__ == '__main__':
    app.run(debug=True)