import urllib.request
from bs4 import BeautifulSoup


def get_page():
    req = urllib.request.Request('http://polkrug.ru/news/gorod/gorodskaya-sreda/8281-uralskoe-kachestvo')
    with urllib.request.urlopen(req) as response:
        code = response.read()
    soup = BeautifulSoup(code, 'html.parser')
    print(soup.prettify())

get_page()