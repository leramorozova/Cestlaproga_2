#  Это файл для всяких функций, которые делают содержания для страничек

# to do:
# 1. кудри (and others pluralia tantum в переводчике прил)
# 2. чек полного переводчика на распарсенной странице
# 3. Страница с переведенным текстом в бутстрапе
# 4. Викторина (адд)
# 5. What should I fuckin' do with FLASK???

import urllib.request
from urllib import parse
import re
from pymystem3 import Mystem
from bs4 import BeautifulSoup  # вот это мировой модуль aka как распарсить хтмл за пару минут и две строчки
                               # (только надо установить, вот документация # https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
m = Mystem()

print('Sorry! Pymystem3 is convenient for the work, but its processing may take much time.\nBe patient, please.\n')


# Нахожу на яндексе погоду в Скопье, в ретурне градусы (без символа градусов цельсия)
def weather():
    req = urllib.request.Request('https://yandex.ru/pogoda/10463')
    with urllib.request.urlopen(req) as response:
        code = response.read().decode('UTF-8')
    reg = re.search('<span class="temp__value">(.*?)</span>', code, flags=re.DOTALL)
    current_weather=reg.group(1)
    return current_weather

# Немного магии или как полностью распарсить страницу без регистрации, смс и 100500 строк регулярок
# И без знаков препинания тоже :с
def main_page():
    req = urllib.request.Request('https://sports.ru/')
    with urllib.request.urlopen(req) as response:
        code = response.read().decode('UTF-8')
    soup = BeautifulSoup(code, 'html.parser')
    text = soup.get_text()
    rus = re.findall('[А-ЯЁа-яё ]{3,}', text)
    html_clean = ' '.join(rus)
    html_clean = re.sub('\s{2,}', '\n', html_clean)
    with open('html_clean.txt', 'w', encoding='UTF-8') as file:
        text = file.write(html_clean)
    return html_clean

# 10 самых частотных слов со страницы sports.ru, в ретурне их массив
def top(html_clean):
    d = {}
    html_lower = html_clean.lower()
    mass = html_lower.split()
    for el in mass:
        if el in d:
            d[el] += 1
        else:
            d[el] = 1
    val = []
    for el in d:
        val.append(d[el])
    top = []
    for i in range(10):
        maxim = max(val)
        for k, v in d.items():
            if v == maxim:
                if k not in top:
                    top.append(k)
                    d.pop(k)
                break
        val.remove(maxim)
    return top

# Это парсер, он вытаскивает из кода страницы пары слов и сразу записывает их в таблицу dict
# Я вызываю эту функцию в краулере (проделываю эту операцию над каждой страницей)
def parcer(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        code = response.read().decode('Windows-1251')
    soup = BeautifulSoup(code, 'html.parser')
    td = soup.find_all('td')
    # отсюда начинаются лютое шаманство и уродливые костыли (но зато работает)))))
    data = td[69:3257]
    s = ''
    for el in data:
        s += str(el) + '\n'
    soup = BeautifulSoup(s, 'html.parser')
    words = soup.get_text()
    mass = words.split('\n')
    clean_mass = []  # в этом массиве просто в кучу все слова со страницы словаря
    # четные - современные, нечетные - перевод на д-нную орфографию
    # тут есть немного мусора, но он не мешает
    for word in mass:
        if '\xa0' not in word and len(word) != 1:
            if word != '' and word != '\xa0' and word != '^':
                only_word = word.split(' ')
                lex = only_word[0].strip(',')
                clean_mass.append(lex.strip('\''))
    for i in range(len(clean_mass)-1):
        if i%2 == 0:
            with open('dict.csv', 'a', encoding='utf-8') as file:
                text = file.write(clean_mass[i] + ',' + clean_mass[i+1] + '\n')  # в этом файле будет весь словарь целиком
            file.close()

# Это краулер, тут я хожу по страницам словаря и собираю слова парсером
def crawler():
    req = urllib.request.Request('http://www.dorev.ru/ru-index.html?l=c0')
    with urllib.request.urlopen(req) as response:
        code = response.read().decode('Windows-1251')
    reg = re.findall('<a href="(ru-index.html\?l=.*?)">', code)
    links = set(reg)
    for link in links:
        parcer('http://www.dorev.ru/'+link)

# Превращаю файл в питоновский объект, который буду использовать в переводчике
def dictionary():
    d = {}
    with open('dict.csv', 'r', encoding='utf-8') as file:
        text = file.read()
    mass = text.split('\n')
    for el in mass:
        mini_mass = el.split(',')
        d[mini_mass[0]] = mini_mass[-1]
    return d

# Исправляю прилагательные
# В женском и среднем родах окончание -iе меняется на -ія, -ые на -ыя, -іеся на -іяся, в мужском же роде они
# остаются неизменными
def adj_trans(word1, word2):
    if word1[-3:] == 'еся':
        return [word1[:-3]+'яся', word2]
    else:
        an_word1=m.analyze(word1)
        for el in an_word1:
            if 'analysis' in el:
                analyz1 = el['analysis']
        an_word2 = m.analyze(word2)
        for el in an_word2:
            if 'analysis' in el:
                analyz2 = el['analysis']
        try:
            if 'A' in analyz1[0]['gr'] and 'им' in analyz2[0]['gr']:
                if 'муж' in analyz2[0]['gr']:
                    return [word1, word2]
                else:
                    if 'мн' in analyz1[0]['gr']:
                        lemma = m.lemmatize(word1)[0]
                        return [lemma[:-1] + 'я', word2]
                    else:
                        return [word1, word2]
            else:
                return [word1, word2]
        except IndexError:
            return [word1, word2]

# Расставляю яти в дативе и аблативе, использую эту ф-цию в translator
def yat_dativus(word):
    info = m.analyze(word)
    if 'analysis' in info[0]:
        wordform = info[0]['analysis']
        for arr in wordform:
            if "пр,ед" in arr['gr'] or "дат,ед" in arr['gr']:
                if "A" not in arr['gr']:
                    return word[:-1]+'ѣ'
                else:
                    return word
            else:
                return word
    else:
        return word

# Переводчик лексем в косвенных формах
def use_of_dict(word):
    lemma = m.lemmatize(word)[0]
    if lemma not in dictionary() or len(word) < 2:
        return word
    else:
        found = dictionary()[lemma]
        difference = len(word) - len(found)
        if difference != 0:
            if difference > 0:
                return found[:-difference] + word[-difference-1:]
            else:
                return found
        else:
            if word[-2] == found[-2]:
                return found[:-1]+word[-1:]
            else:
                return found[:-2]+word[-2:]

# Комплексный переводчик существительных и прочего (i + яти + з/с + словарные формы)
def main_translator(word):
    try:
        word = use_of_dict(word)
        vowels = 'йуеиыаоэяюё'
        consonants = 'цкнгшщзхфвпрлджчсмтб'
        for letter in range(len(word)-1):  # меняем и на i
            if word[letter] == 'и' and word[letter + 1] in vowels:
                word = word[:letter] + 'i' + word[letter + 1:]
            elif word[letter] == 'И' and word[letter + 1] in vowels:
                word = word[:letter] + 'I' + word[letter + 1:]
        word = yat_dativus(word)
        if word[len(word) - 1] in consonants:  # добавляем ъ в конце слов
            word += 'ъ'
        if word.startswith('чрес') or word.startswith('чрес') or word.startswith('черес'):
            word = re.sub('(бе|чре|чере)c', '\\1з', word)
        return word
    except TypeError:
        return word

# Собрала все в кучу и перевожу весь текст
def text_translation():
    with open('html_clean.txt', 'r', encoding='UTF-8') as file:
         text = file.read()
         mass = text.split()
    # print('Translating of adjectives is processing...')
    # for i in range(0, len(mass)-1):
    #     collocation = adj_trans(mass[i], mass[i + 1])
    #     mass[i], mass[i + 1] = collocation[0], collocation[1]  # пары прил + сущ переприсваиваются здесь
    #     print(mass[i], mass[i + 1])
    #     print ('(' + str(i + 1) + '/' + str(len(mass)) + ')')
    #with open('translated.txt', 'w', encoding='UTF-8') as file: #  перестраховка
    #    text = file.write(' '.join(mass))
    print('Adjectives are translated, dealing with nouns...')
    for i in range(0, len(mass)):
        translated_word = main_translator(mass[i])
        if translated_word != None:
            mass[i] = translated_word  # а существительные - здесь
        else:
            mass[i] == 'ЧМ'  #  жутко извиняюсь за этот костыль, у меня почему-то в через use_of dict не проходит
                             #  только эта лексема
        print('(' + str(i + 1) + '/' + str(len (mass)) + ')')
        print(' '.join(mass))
    print('Translation is finished!')
    print(' '.join(mass))
    with open('translated.txt', 'w', encoding='UTF-8') as file:
        text = file. write(' '.join(mass))

text_translation()

def main():
    crawler()
    text_translator()
