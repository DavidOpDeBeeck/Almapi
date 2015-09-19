#!flask/bin/python
import utilities
from datetime import date
from json import dumps
from flask import Flask, Response

app = Flask(__name__)

@app.route('/almas', methods=['GET'])
def web_get_all_almas():
    return Response(dumps(utilities.get_all_almas()), mimetype='application/json')

@app.route('/almas/<int:alma_id>', methods=['GET'])
def web_get_specific_alma(alma_id):
    return Response(dumps(utilities.get_alma(alma_id)), mimetype='application/json')

@app.route('/almas/<int:alma_id>/menu', methods=['GET'])
def web_get_specific_alma_menu_from_current_week(alma_id):
    return Response(dumps(utilities.get_menu(alma_id, date.today().year, date.today().isocalendar()[1])), mimetype='application/json')

@app.route('/almas/<int:alma_id>/menu/<int:week_id>', methods=['GET'])
def web_get_specific_alma_menu_from_specific_week(alma_id, week_id):
    return Response(dumps(utilities.get_menu(alma_id, date.today().year, week_id)), mimetype='application/json')

@app.route('/almas/<int:alma_id>/menu/<int:week_id>/<int:year_id>', methods=['GET'])
def web_get_specific_alma_menu_from_specific_week_and_specific_year(alma_id, week_id, year_id):
    return Response(dumps(utilities.get_menu(alma_id, year_id, week_id)), mimetype='application/json')

@app.errorhandler(404)
def not_found(error):
    resp = Response(dumps({'error': str(error)}), mimetype='application/json')
    resp.status_code = 404
    return resp

@app.errorhandler(500)
def internal_server_error(error):
    resp = Response(dumps({'error': str(error)}), mimetype='application/json')
    resp.status_code = 500
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0')
