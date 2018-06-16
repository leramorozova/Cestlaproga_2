import re
import os
from collections import defaultdict
import random
import tweepy


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
    for file in os.listdir('./texts'):
        with open('tokens.txt', 'a', encoding='UTF-8') as data:
            with open('./texts/' + file, 'r', encoding='UTF-8') as text:
                content = text.read().lower()
                content = re.sub('[«»()]', '', content)
                token_list = content.split()
                for i in token_list:
                    if i[-1] in '.,:;?!…' and i[-1] not in '1234567890':
                        text = data.write(i[:-1] + '\n' + i[-1] + '\n')
                    elif i[-2:] == '?!':
                        text = data.write(i[:-2] + '\n' + i[-2] + '\n')
                    elif i[-3:] == '...':
                        text = data.write(i[:-3] + '\n' + i[-3] + '\n')
                    else:
                        text = data.write(i + '\n')
        data.close()


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
    with open('tokens.txt', 'r', encoding='UTF-8') as data:
        tokens = data.read().split('\n')
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
    return model


def generate_sentence():
    model = trigramizer()
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


API_KEY = "CFvvE8BNcONOSGopm5UAphRdR"
API_SECRET = "AtWO6LIGP4XfuGW6OVegZIYh36Se8ySd9fNk4O8crORU3nPYfy"

ACCESS_TOKEN = "1006262723691405313-Bvg2U7D6daqNqjgOvA5w8xiqzukQoc"
ACCESS_TOKEN_SECRET = "OC2UP4JR4gedwvXQbrR2dbLFLJEtDTeNRVev3L8NRsa4r"


def tweet():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    api.update_status(validation(generate_sentence()))