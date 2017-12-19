import os

file = open(os.path.join('..', 'HW3', 'templates', 'json.txt'), 'r', encoding='utf-8')
text = file.read()
print(text)