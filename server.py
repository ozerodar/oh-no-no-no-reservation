from flask import Flask
from flask import request, jsonify
import json

app = Flask(__name__)

def my_super_post_method():
    return "POST Success"

@app.route('/thepostthepost/<shark_name>', methods=['GET', 'POST'])
def login(shark_name):
    if request.method == 'POST':
        return jsonify({"argument_was": shark_name})
    else:
        return jsonify({"argument_was": 'None'})


@app.route('/postjson/', methods=['GET', 'POST'])
def post_json():
    if request.method == 'POST':
        received_json = request.get_json()
        print(json.loads(received_json))
        return jsonify({"json_arg": "stuff"})
    else:
        return "post_json called without POST"

@app.route('/')
def hello_world():
    return 'Hello, World!'