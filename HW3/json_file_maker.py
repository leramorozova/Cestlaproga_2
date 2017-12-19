import json

def obj_maker():
    mass=[]
    file = open(os.path.join('..', 'HW3', 'metadata.csv'), 'r', encoding='utf-8')
    text = file.read()
    text=text.split('\n')
    for line in text:
        if line != '':
            ank=line.split(',')
            d = {"name": ank[0], "surname": ank[1], "secname": ank[2], "birthyear": ank[3], "education": ank[4],
                "home": ank[5], "lang": ank[6], "answer1": ank[7], "answer2": ank[8]}
            mass.append(d)
    file.close()
    j_obj = json.dumps(mass, ensure_ascii = False, sort_keys = True, indent = 4)
    return j_obj

def file_maker():
    file = open(os.path.join('..', 'HW3', 'templates', 'json.txt'), 'w', encoding='utf-8')
    text = file.write(obj_maker())
    file.close()
    return text

def table(j_obj):
    statistics = []
    data = json.loads(j_obj)
    participants = len(data)
    sum_age = 0
    educated = 0
    moscow_livers = 0
    russian = 0
    stress2_nom = 0
    stress2_abl = 0
    for dict in data:
        if dict["home"] == "Москва":
            moscow_livers += 1
        if dict["lang"] == "русский":
            russian += 1
        if dict["education"] == "высшее":
            educated += 1
        sum_age += 2017 - int(dict["birthyear"])
        if dict["answer1"] == "stress2":
            stress2_nom += 1
        if dict["answer2"] == "stress2":
            stress2_abl += 1
    statistics.append(participants)
    av_age = sum_age // participants
    statistics.append(av_age)
    statistics.append(educated)
    statistics.append(moscow_livers)
    statistics.append(russian)
    statistics.append(stress2_nom)
    statistics.append(stress2_abl)
    return statistics

def pyfile_maker():
    data = json.loads(obj_maker())
    return data