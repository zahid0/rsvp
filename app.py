from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/content')
def content():
    with open('data.txt', 'r') as file:
        content = file.read().replace('\n', ' <br> ')

    return jsonify({'content': content.split()})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
