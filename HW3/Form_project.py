import json
from flask import Flask
from flask import url_for, render_template, request, redirect
import json_file_maker

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/thanks')
def thanks():
    if request.args:
        name = request.args['name']
        surname = request.args['surname']
        secname = request.args['secname']
        birthyear = request.args['birthyear']
        education = request.args['education']
        home = request.args['home']
        lang = request.args['lang']
        answer1 = request.args['answer1']
        answer2 = request.args['answer2']
        data(name, surname, secname, birthyear, education, home, lang, answer1, answer2)
    return render_template('thanks.html')

obj=[]

def data(name, surname, secname, birthyear, education, home, lang, answer1, answer2):
    table = open('metadata.csv', 'w', encoding = 'utf-8')
    line=name + ',' + surname + ',' + secname + ',' + birthyear+',' + education + ',' + home + ',' + lang + \
         ',' + answer1 + ','+answer2
    global obj
    obj.append(line)
    for el in obj:
        text = table.write(el+'\n')
    table.close()

@app.route('/json')
def json():
    json_file_maker.file_maker()
    return render_template('json.txt')

@app.route('/stats')
def stats():
    data = json_file_maker.table(json_file_maker.obj_maker())
    participants = data[0]
    av_age = data[1]
    educated = data[2]
    moscow_livers = data[3]
    russian = data[4]
    stress2_nom = data[5]
    stress2_abl = data[6]
    return render_template('stats.html', participants = participants, av_age = av_age, educated = educated,
                           moscow_livers = moscow_livers, russian = russian, stress2_nom = stress2_nom, stress2_abl = stress2_abl)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/results')
def results():
    if request.args:
        city = request.args['city']
        data = json_file_maker.pyfile_maker()
        names = {}
        cities = []
        for dict in data:
            cities.append(dict["home"])
        if city not in cities:
            return redirect('/not_found')
        else:
            for dict in data:
                if dict["home"] == city:
                    name = dict["surname"] + ' ' + dict["name"] + ' ' + dict["secname"]
                    names[name] = "(возраст: " + str(2017 - int(dict["birthyear"])) + ")"
            return render_template('results.html', names=names)

@app.route('/not_found')
def not_found():
    return render_template ('not_found.html')

if __name__ == '__main__':
    app.run(debug=True)