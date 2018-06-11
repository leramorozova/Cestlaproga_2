import re
import os
import sqlite3
from collections import defaultdict
import pickle
import random

conn = sqlite3.connect('tokens.db')
c = conn.cursor()

#  TODO: Замена имен собственных на заглавные буквы из proper names

def proper_names():
    content = ''
    for file in os.listdir('./texts'):
        with open('./texts/' + file, 'r', encoding='UTF-8') as text:
            book = text.read()
            content += book
    nomens = re.findall('[a-яА-Я] [А-Я][а-я]+', content)
    nomens = set([el[2:] for el in nomens])
    with open('names.txt', 'a', encoding='UTF-8') as file:
        for el in nomens:
            text = file.write(el + '\n')
    return nomens


def tokenizer():
    c.executescript("""DROP TABLE IF EXISTS tokens;
                       CREATE TABLE tokens
                       (token TEXT);
                        """)
    for file in os.listdir('./texts'):
        with open('./texts/' + file, 'r', encoding='UTF-8') as text:
            content = text.read().lower()
            content = re.sub('[«»()]', '', content)
            token_list = content.split()
            for i in token_list:
                if i[-1] in '.,:;?!…':
                    c.execute('''INSERT INTO tokens (token) 
                                                 VALUES (?)''', [i[:-1]])
                    c.execute('''INSERT INTO tokens (token) 
                                  VALUES (?)''', [i[-1]])
                elif i[-2:] == '?!':
                    c.execute('''INSERT INTO tokens (token) 
                                      VALUES (?)''', [i[:-2]])
                    c.execute('''INSERT INTO tokens (token) 
                                 VALUES (?)''', [i[-2:]])
                elif i[-3:] == '...':
                    c.execute('''INSERT INTO tokens (token) 
                                     VALUES (?)''', [i[:-3]])
                    c.execute('''INSERT INTO tokens (token) 
                                                     VALUES (?)''', [i[-3:]])
                else:
                    c.execute('''INSERT INTO tokens (token) 
                                 VALUES (?)''', [i])
    conn.commit()


def gen_trigrams(tokens):
    t0, t1 = '$', '$'
    for t2 in tokens:
        yield t0, t1, t2
        if t2 in '.!?':
            yield t1, t2, '$'
            yield t2, '$', '$'
            t0, t1 = '$', '$'
        else:
            t0, t1 = t1, t2


def trigramizer():
    c.execute('''SELECT token FROM tokens''')
    tokens = [el[0] for el in c.fetchall()]
    trigrams = gen_trigrams(tokens)

    bi, tri = defaultdict(lambda: 0.0), defaultdict(lambda: 0.0)

    for t0, t1, t2 in trigrams:
        bi[t0, t1] += 1
        tri[t0, t1, t2] += 1

    model = {}
    for (t0, t1, t2), freq in tri.items():
        if (t0, t1) in model:
            model[t0, t1].append((t2, freq / bi[t0, t1]))
        else:
            model[t0, t1] = [(t2, freq / bi[t0, t1])]
    with open('model.pickle', 'wb') as data:
        pickle.dump(model, data)
    return model


def generate_sentence():
    with open('model.pickle', 'rb') as file:
        model = pickle.load(file)
    phrase = ''
    t0, t1 = '$', '$'
    while 1:
        t0, t1 = t1, random.choice(model[t0, t1])[0]
        if t1 == '$':
            break
        if t1 in '.!?,;:…' or t0 == '$':
            phrase += t1
        else:
            phrase += ' ' + t1
    return phrase.split()


def validation(sentence):
    with open('names.txt', 'r', encoding='UTF-8') as file:
        data = file.read()
    proper_names = data.split('\n')
    for i, word in enumerate(sentence):
        if word.capitalize() in proper_names:
            sentence[i] = sentence[i].capitalize()
    sentence[0] = sentence[0].capitalize()
    return ' '.join(sentence)


for i in range(100):
    print(validation(generate_sentence()))
