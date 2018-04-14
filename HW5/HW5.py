import urllib.request
import json
import sqlite3
import matplotlib.pyplot as plt


def posts():  # скачиваю посты
    offsets = [0, 100, 200, 300]
    conn = sqlite3.connect('vkapi.db')
    c = conn.cursor()
    c.executescript("""DROP TABLE IF EXISTS posts;

                            CREATE TABLE posts
                            (post_id TEXT, 
                             post TEXT);
                    """)
    for off in offsets:
        req = urllib.request.Request('https://api.vk.com/method/wall.get?owner_id=-113752011&v=5.74&access_token=8423c2448423c2448423c244d08441f2a1884238423c244dee1644d9e90529494134bf8&count=100&offset=' + str(off))
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        data = json.loads(result)
        for item in data['response']['items']:
            c.execute('''
                    INSERT INTO posts (post_id, post) 
                    VALUES (?, ?)
                        ''', [item['id'], item['text']])
    conn.commit()
    conn.close()


def comments():  # скачиваю комментарии к постам
    conn = sqlite3.connect('vkapi.db')
    c = conn.cursor()
    c.executescript("""
                        DROP TABLE IF EXISTS comments;

                        CREATE TABLE comments
                                (post_id TEXT,
                                 comment TEXT, 
                                 user_id TEXT);
                        """)
    c.execute('''SELECT post_id
                 FROM posts ''')
    result = c.fetchall()
    for i in result:
        offsets = [0, 100, 200]
        for off in offsets:
            req = urllib.request.Request('https://api.vk.com/method/wall.getComments?owner_id=-113752011&post_id=' + i[0] + '&v=5.74&access_token=8423c2448423c2448423c244d08441f2a1884238423c244dee1644d9e90529494134bf8&count=100&offset=''' + str(off))
            response = urllib.request.urlopen(req)
            result = response.read().decode('utf-8')
            data = json.loads(result)
            for item in data['response']['items']:
                c.execute('''
                        INSERT INTO comments (post_id, comment, user_id) 
                        VALUES (?, ?, ?)
                            ''', [i[0], item['text'], item['from_id']])
    conn.commit()
    conn.close()


def socio_info():  # скачиваю личную информацию каждого комментатора
    conn = sqlite3.connect('vkapi.db')
    c = conn.cursor()
    c.executescript("""
                            DROP TABLE IF EXISTS socio;

                            CREATE TABLE socio
                                    (user_id TEXT,
                                     comment_length TEXT, 
                                     city TEXT,
                                     age TEXT);
                            """)
    c.execute('''SELECT user_id, comment
                     FROM comments ''')
    result = c.fetchall()
    for el in result:
        comment_length = len(el[1])
        if el[0][0] == '-':
            usrid = el[0][1:]
        else:
            usrid = el[0]
        req = urllib.request.Request(
            'https://api.vk.com/method/users.get?user_id=' + usrid + '&fields=bdate,city&v=5.74&access_token=8423c2448423c2448423c244d08441f2a1884238423c244dee1644d9e90529494134bf8')
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        data = json.loads(result)
        try:
            date = data['response'][0]['bdate']
            date = date.split('.')
            if len(date[-1]) == 4:
                age = 2018 - int(date[-1])
            else:
                age = ''
        except KeyError:
            age = ''
        try:
            city = data['response'][0]['city']['title']
        except KeyError:
            city = ''
        c.execute('''
                     INSERT INTO socio (user_id, comment_length, city, age) 
                     VALUES (?, ?, ?, ?)
                     ''', [usrid, comment_length, city, age])
    conn.commit()
    conn.close()


def plots():  # рисую графики
    age_length = {}
    city_length = {}
    conn = sqlite3.connect('vkapi.db')
    c = conn.cursor()
    c.execute('''SELECT comment_length, city, age
                         FROM socio ''')
    result = c.fetchall()
    for el in result:
        if el[2] in age_length:
            age_length[el[2]].append(int(el[0]))
        else:
            age_length[el[2]] = [int(el[0])]
        if el[1] in city_length:
            city_length[el[1]].append(int(el[0]))
        else:
            city_length[el[1]] = [int(el[0])]
    for i in age_length:
        age_length[i] = sum(age_length[i]) // len(age_length[i])
    for i in city_length:
        city_length[i] = sum(city_length[i]) // len(city_length[i])
    age_length.pop('')
    city_length.pop('')
    conn.commit()
    conn.close()
    plt.figure(figsize=(30, 10))
    plt.bar(age_length.keys(), age_length.values())
    plt.title('Отношение возраста к длине комментария')
    plt.xlabel('AGE')
    plt.ylabel('AVERAGE LENGTH')
    plt.savefig('age-length.png', format='png', dpi=100)
    plt.clf()
    plt.figure(figsize=(30, 10))
    plt.bar(city_length.keys(), city_length.values())
    plt.title('Отношение возраста к городу проживания')
    plt.xlabel('CITY')
    plt.ylabel('AVERAGE LENGTH')
    plt.xticks(range(len(city_length.keys())), city_length.keys(), rotation=90)
    plt.savefig('city-length.png', format='png', dpi=100)

# Городов слишком много, мне никак не сделать это красиво :(

def len_post():  # совсем забыла про длины постов: