import HW_add_content
from flask import Flask
from flask import url_for, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def form():
    temperature=HW_add_content.weather()
    return render_template('form.html', temperature=temperature)

if __name__ == '__main__':
    app.run(debug=True)
