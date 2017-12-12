# Вам дана база данных со словами из хеттского корпуса (в приложении) и расшифровка глосс.
# Таблица называется wordforms, имена полей: Lemma, Wordform, Glosses.
#
# Нужно извлечь из неё данные и на них построить новую многотабличную реляционную базу с тремя таблицами: слова
# (id, Lemma, Wordform, Glosses), глоссы (id, обозначение, расшифровка) и слова-глоссы (id слова, id глоссы).
# Глоссы из соответствующего поля требуется разбить на отдельные элементы (разбиваются по точке).
#
# Нужно посчитать и визуализировать на графике все глоссы.

import sqlite3
import matplotlib
import matplotlib.pyplot as plt

conn = sqlite3.connect('hittite.db')
c = conn.cursor()

def sql_updater():
    c.execute('''SELECT Glosses FROM wordforms''')
    gl=c.fetchall()
    gloss_split=[]
    for cor in gl:
        for gloss in cor:
            g_s=gloss.split('.')
            gloss_split.append(' '.join(g_s))

    c.executescript('''DROP TABLE IF EXISTS words;

        CREATE TABLE IF NOT EXISTS words
        (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Lemma TEXT,
        Wordform TEXT,
        Glosses TEXT);
        ''')

    c.execute('''INSERT INTO words (Lemma, Wordform, Glosses)
        SELECT Lemma, Wordform, Glosses FROM wordforms;
        ''')

    for i in range(len(gloss_split)):
        c.execute('''
    UPDATE words
    SET Glosses = ?
    WHERE id = ?''', [gloss_split[i], i+1])

    c.executescript('''DROP TABLE IF EXISTS glosses;

        CREATE TABLE IF NOT EXISTS glosses
        (id INTEGER,
        Gloss TEXT,
        Meaning TEXT);
        ''')

    with open ('Glossing_rules.txt', 'r', encoding='UTF-8') as file:
        content=file.read()
    mass=content.split('\n')
    gloss=[]
    meaning=[]
    for i in mass:
        items=i.split(' — ')
        gloss.append(items[0])
        meaning.append(items[1])

    for i in range(1, len(gloss)+1):
        c.execute('INSERT INTO glosses (id, Gloss, Meaning) VALUES (?, ?, ?)',
              [i, gloss[i-1], meaning[i-1]])

    c.executescript('''DROP TABLE IF EXISTS words_glosses;

        CREATE TABLE IF NOT EXISTS words_glosses
        (id_word INTEGER,
        id_gloss INTEGER);
        ''')

    c.execute('SELECT id, Glosses FROM words')
    word_glosses = c.fetchall()
    c.execute('SELECT id, Gloss FROM glosses')
    dict_glosses = c.fetchall()
    for corr in word_glosses:
        corr_split=corr[1].split(' ')
        for el in corr_split:
            for item in dict_glosses:
                if el==item[1]:
                    c.execute('INSERT INTO words_glosses (id_word, id_gloss) VALUES (?, ?)',
                          [corr[0], item[0]])

    c.execute('SELECT id_word FROM words_glosses')
    nums=c.fetchall()
    words=[]
    for cor in nums:
        for el in cor:
            words.append(el)
    for i in range(1, 528):
        if i in words:
            continue
        else:
            c.execute('INSERT INTO words_glosses (id_word, id_gloss) VALUES (?, ?)',
                  [i, 'No gloss'])
    conn.commit()
    return print('data base is updated successfully')

def graf():
    stat_d={}
    c.execute('SELECT * FROM words_glosses ORDER BY id_gloss')
    mass=c.fetchall()
    for cor in mass:
        if cor[1] in stat_d:
            stat_d[cor[1]]+=1
        else:
            stat_d[cor[1]]=1
    for i in range(1, 18):
        if i not in stat_d:
            stat_d[i]=0
    plt.title("Визуализация использования представленных в словаре глосс")
    for key in stat_d:
        plt.scatter(key, stat_d[key], s=100)
        plt.text(key, stat_d[key]+1, key)
    plt.savefig('gloss_visualisation.pdf') # если хотите файл с графиком
    return print('figure is created successfully')

sql_updater() # добавление таблиц в словарь
graf() # рисование графика
plt.show() # если хотите полюбоваться на график
conn.close()