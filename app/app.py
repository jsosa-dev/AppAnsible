from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Hola, Mundo!"

if __name__ == '__main__':
    app.run(debug=True)