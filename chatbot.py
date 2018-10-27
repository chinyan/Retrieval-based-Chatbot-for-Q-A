from flask import Flask, render_template
from flask import request, Response
from json import dumps
from StackOverflow_Word2Vec import *

language = ""
text = ''

app = Flask(__name__)
app.config['debug'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_language/', methods=['GET', 'POST'])
def get_language():
    language = request.get_json(silent=True)
    print("get language")
    print(language)

    global text
    text = TextProcessing(language)

    return Response(response=dumps(language, ensure_ascii=False, allow_nan=True),
                    status=200,
                    mimetype='application/json')


@app.route('/get_message/', methods=['GET', 'POST'])
def get_message():
    input_msg = request.get_json(silent=True)
    print(input_msg)

    for col, vals in input_msg.items():
        if col == "MESSAGE":
            input = vals

    message, response, top_five = text.Main(input)
    print(message)
    print(response)
    json_output = {
        "MESSAGE": message,
        "RESPONSE": response,
        "TOP_FIVE": top_five,
    }
    return Response(response=dumps(json_output, ensure_ascii=False, allow_nan=True),
                    status=200,
                    mimetype='application/json')


if __name__ == "__main__":
    app.run(host='localhost', port=8000)
