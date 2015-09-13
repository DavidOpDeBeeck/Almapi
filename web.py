#!flask/bin/python
from flask import Flask
import utils
import json

app = Flask(__name__)


# WEB FUNCTIONS

@app.route('/almas', methods=['GET'])
def web_get_all_almas():
    return json.dumps(utils.get_all_almas())


@app.route('/almas/<int:alma_id>', methods=['GET'])
def web_get_alma(alma_id):
    return json.dumps(utils.get_alma(alma_id))


@app.route('/almas/<int:alma_id>/menu', methods=['GET'])
def web_get_alma_menu(alma_id):
    return json.dumps(utils.get_menu(alma_id))


if __name__ == '__main__':
    app.run(debug=True)
