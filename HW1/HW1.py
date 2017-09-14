import urllib.request
import re

def download_page():
    req = urllib.request.Request('http://www.vecherniyorenburg.ru/')
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    return html

def title_list():
    page=download_page()
    reg1=re.compile('<div class="news-name"><a href=".+">.+</a></div>')
    reg2=re.compile('" title=".+"></a> </div>')
    titles=reg1.findall(page)+reg2.findall(page)
    clean_titles=[]
    for el in titles:
        clean_el=re.sub('<.*?>|[a-z">=]', '', el)
        clean_titles.append(clean_el)
    return clean_titles

def create_file():
    titles = open('list.txt', 'w', encoding='utf-8')
    for el in title_list():
        text = titles.write(el + '\n')

create_file()
print('Done')
