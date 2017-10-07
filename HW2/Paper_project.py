import urllib.request
import re
import os
import shutil
import time


def download_page(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        code = response.read().decode('Windows-1251')
    info=search_info(code)
    pieces=info.split('\n')
    au=pieces[0][4:]
    ti=pieces[1][4:]
    date=pieces[2][4:]
    topic = pieces[3][7:]
    file_name=url[-2:]+date+'.txt'
    file=open(file_name, 'w', encoding='Windows-1251')
    text=file.write(info)
    text=file.write('@url '+url+'\n')
    clean_text= code_cleaner(code)
    text=file.write(clean_text)
    path = os.path.join('.', 'Zvezda', 'plain', str(date[-4:]), str(date[-7:-5]), file_name)
    row = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'
    line='\n'+row % (path, au, '', ' ', ti, date, 'публицистика', ' ', ' ', topic, ' ', 'нейтральный', 'н-возраст', 'н-уровень', 'краевая', url, 'Звезда', ' ', str(pieces[2][-4:]), 'газета', 'Россия', 'Пермский край', 'ru')
    return line


def search_info(code):
    reg_au=re.search('</P>.*?<P>.*?<STRONG>(.*?)</STRONG>', code, flags=re.DOTALL)
    if reg_au!=None:
        au=reg_au.group(1)
        if au=='»»»':
            au='Noname'
    else:
        au='Noname'
    reg_ti=re.search('<h1>(.*?)</h1>', code, flags=re.DOTALL)
    if reg_ti!=None:
        ti=reg_ti.group(1)
    else:
        ti='Notitle'
    reg_da=re.search('<div class="date_bg"><span>.*?</span>.*?<span>(.*?)(&nbsp)?</span>', code, flags=re.DOTALL)
    if reg_da!=None:
        da=reg_da.group(1)[:8]
        pieces=da.split('.')
        pieces[2]='20'+pieces[2]
        da='.'.join(pieces)
    else:
        da='Nodate'
    reg_topic=re.search('<a href="/news/\?razdel=.*?">(.*?)</a>', code, flags=re.DOTALL)
    if reg_topic!=None:
        topic=reg_topic.group(1)
    else:
        topic='Nodate'
    info='@au '+au+'\n'+'@ti '+ti+'\n'+'@da '+da+'\n'+'@topic '+topic+'\n'
    return info


def code_cleaner(code):
    html_clean = re.sub('<.*?>', ' ', code, flags=re.DOTALL)
    html_clean = re.sub(';?&ndash;?', '–', html_clean)
    html_clean = re.sub(';?&nbsp;?', ' ', html_clean)
    html_clean = re.sub(';?&laquo;?', '«', html_clean)
    html_clean = re.sub(';?&raquo;?', '»', html_clean)
    html_clean = re.sub(';?&nbsp;?', ' ', html_clean)
    html_clean = re.sub(';(l|r)arr;?', ' ', html_clean)
    html_clean = re.sub('[0-9a-zA-Z\\/\(\)\-\'\{\}\+_=:;\[\]\.,\|\&\?" ]{5,}', ' ', html_clean)
    html_clean = re.sub('({|}|>|@|--|;|\$|\)|\(|%|»»»)', ' ', html_clean)
    html_clean = re.sub('\s{2,}', '\n', html_clean, flags=re.DOTALL)
    return html_clean


def crawler():
    table = open('metadata.csv', 'w', encoding='Windows-1251')
    line = table.write('path\tauthor\tsex\tbirthday\theader\tcreated\tsphere\tgenre_fi\ttype\ttopic\tchronotop\tstyle\taudience_age\taudience_level\taudience_size\tsource\tpublication\tpublisher\tpubl_year\tmedium\tcountry\tregion\tlanguage')
    site_name = 'http://www.zwezda.perm.ru/news/?pub='
    for i in range(3677, 5333):
        time.sleep(5)
        url = site_name + str(i)
        line=table.write(download_page(url))
    return table


def put_in_right_folder():
    os.makedirs(os.path.join('.','trash'))
    lst = os.listdir('.')
    for file in lst:
        if file[-4:]=='.txt':
            files_for_stemming(file)
    for i in range(10, 18):
        for q in range(1, 13):
            if len(str(q)) == 1:
                m = '0' + str(q)
            else:
                m = str(q)
            os.makedirs(os.path.join('.', 'Zvezda', 'plain', '20' + str(i), m))
            os.makedirs(os.path.join('.', 'Zvezda', 'mystem-xml', '20'+str(i), m))
            os.makedirs(os.path.join('.', 'Zvezda', 'mystem-plain', '20'+str(i), m))
    for file in lst:
        if file[-4:]=='.txt':
            year = file[-8:-4]
            if year == 'date':
                continue
            month = file[-11:-9]
            shutil.move(os.path.join('.'),file), os.path.join('.' 'Zvezda', 'plain', year, month)
        if file == 'metadata.csv':
                shutil.move(os.path.join('.', 'metadata.csv'), os.path.join('.', 'Zvezda'))


def stemming():
    inp='./trash'
    lst = os.listdir(inp)
    for fl in lst:
        pieces=fl.split('.')
        number=pieces[2][:4]+'/'+pieces[1]
        os.system(r"/home/lera/ms/mystem -i -n -e Windows-1251 " + inp + os.sep + fl + " ./Zvezda/mystem-plain/" + str(number) + os.sep + fl)
        os.system(r"/home/lera/ms/mystem -i -n -d -e Windows-1251 --format xml  " + inp + os.sep + fl + " ./Zvezda/mystem-xml/" + str(number) + os.sep + fl)


# за эту функцию очень извиняюсь, но у меня почему-то не сработал ---format xml, и пришлось крутиться

def xml_maker():
    for i in range (10,18):
        for q in range(1, 13):
            if len(str(q)) == 1:
                m = '0' + str(q)
            else:
                m = str(q)
            dir=os.path.join('.', 'Zvezda', 'mystem-xml', '20'+str(i), m)
            lst = os.listdir(dir)
            for file_name in lst:
                pieces=file_name.split('.')
                os.rename(os.path.join(dir, file_name), os.path.join(dir, '.'.join(pieces[0:2]) +'.' +pieces[2][:4]+'.xml'))


def files_for_stemming(file):
    pieces = file.split('.')
    with open(file, 'r', encoding='Windows-1251') as file:
        text = file.read()
        lines = text.split('\n')
        new_lines = lines[6:]
    file_name='.'.join(pieces[0:3]) + '-1' + '.txt'
    text_for_stem = open(file_name, 'w', encoding='Windows-1251')
    article = text_for_stem.write('\n'.join(new_lines))
    shutil.move(os.path.join('.', file_name), os.path.join('.', 'trash'))
    return text_for_stem


#если жизнь и рассудок догори вам, пожалуйста, включайте функции по очереди

def main():
    crawler()
    put_in_right_folder()
    stemming()
    xml_maker()

#main()
stemming()

