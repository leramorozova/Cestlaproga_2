# Вам дана база данных со словами из хеттского корпуса (в приложении) и расшифровка глосс.
# Таблица называется wordforms, имена полей: Lemma, Wordform, Glosses.
#
# Нужно извлечь из неё данные и на них построить новую многотабличную реляционную базу с тремя таблицами: слова
# (id, Lemma, Wordform, Glosses), глоссы (id, обозначение, расшифровка) и слова-глоссы (id слова, id глоссы).
# Глоссы из соответствующего поля требуется разбить на отдельные элементы (разбиваются по точке).
#
# Нужно посчитать и визуализировать на графике все глоссы.

# В этой версии нет третьей таблицы и глоссы не просплиттены, а так все работает.

import sqlite3


with open ('Glossing_rules.txt', 'r', encoding='UTF-8') as file:
    content=file.read()
mass=content.split('\n')
gloss=[]
meaning=[]
for i in mass:
    items=i.split(' — ')
    gloss.append(items[0])
    meaning.append(items[1])


conn = sqlite3.connect('hittite.db')
c = conn.cursor()

c.executescript('''DROP TABLE IF EXISTS words;

        CREATE TABLE IF NOT EXISTS words
        (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Lemma TEXT,
        Wordform TEXT,
        Glosses TEXT);

        INSERT INTO words (Lemma, Wordform, Glosses)
        SELECT Lemma, Wordform, Glosses FROM wordforms;

        DROP TABLE IF EXISTS glosses;

        CREATE TABLE IF NOT EXISTS glosses
        (id INTEGER,
        Gloss TEXT,
        Meaning TEXT);
        ''')

for i in range(1, len(gloss)+1):
    c.execute('INSERT INTO glosses (id, Gloss, Meaning) VALUES (?, ?, ?)',
              [i, gloss[i-1], meaning[i-1]])

c.executescript('''DROP TABLE IF EXISTS words_glosses;

        CREATE TABLE IF NOT EXISTS words_glosses
        (id_word INTEGER,
        id_gloss);
        ''')

conn.close()