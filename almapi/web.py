#!flask/bin/python
from datetime import date
from json import dumps

from flask import Flask, jsonify, make_response

from almapi import utilities

app = Flask(__name__)


@app.route('/almas', methods=['GET'])
def web_get_all_almas():
    return jsonify(utilities.get_all_almas())


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

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Something went wrong'}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
