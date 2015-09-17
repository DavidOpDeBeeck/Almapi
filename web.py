#!flask/bin/python
from datetime import date
from flask import Flask
from json import dumps

import utilities

app = Flask(__name__)


@app.route('/almas', methods=['GET'])
def web_get_all_almas():
    return dumps(utilities.get_all_almas(), indent=4, sort_keys=True)


@app.route('/almas/<int:alma_id>', methods=['GET'])
def web_get_specific_alma(alma_id):
    return dumps(utilities.get_alma(alma_id), indent=4, sort_keys=True)


@app.route('/almas/<int:alma_id>/menu', methods=['GET'])
def web_get_specific_alma_menu_from_current_week(alma_id):
    return dumps(utilities.get_menu(alma_id, date.today().year, date.today().isocalendar()[1]), indent=4, sort_keys=True)


@app.route('/almas/<int:alma_id>/menu/<int:week_id>', methods=['GET'])
def web_get_specific_alma_menu_from_specific_week(alma_id, week_id):
    return dumps(utilities.get_menu(alma_id, date.today().year, week_id), indent=4, sort_keys=True)


@app.route('/almas/<int:alma_id>/menu/<int:week_id>/<int:year_id>', methods=['GET'])
def web_get_specific_alma_menu_from_specific_week_and_specific_year(alma_id, week_id, year_id):
    return dumps(utilities.get_menu(alma_id, year_id, week_id), indent=4, sort_keys=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
