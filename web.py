#!flask/bin/python
from flask import Flask
from datetime import date
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


@app.route('/almas/<int:alma_id>/menu/<int:week_id>', methods=['GET'])
def web_get_alma_menu_from_week(alma_id, week_id):
    return json.dumps(utils.get_menu(alma_id, date.today().year, week_id))


@app.route('/almas/<int:alma_id>/menu/<int:week_id>/<int:year_id>', methods=['GET'])
def web_get_alma_menu_from_week_and_year(alma_id, week_id, year_id):
    return json.dumps(utils.get_menu(alma_id, year_id, week_id))


if __name__ == '__main__':
    app.run(debug=True)
