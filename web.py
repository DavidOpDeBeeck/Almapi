#!flask/bin/python
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# DB VARIABLES

DB_NAME = 'scraper/alma.db'

# DB FUNCTIONS

def open_connection():
    connection = sqlite3.connect(DB_NAME)
    return connection


def close_connection(connection):
    connection.commit()
    connection.close()


def get_all_almas():
    connection = open_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT alma_id,name FROM ALMA;')
    result = cursor.fetchall()
    close_connection(connection)
    response = []
    for alma_index, alma_name in result:
        response.append({
            'id': alma_index,
            'name': alma_name
        })
    return response


def get_alma(alma_id):
    connection = open_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT alma_id,name FROM ALMA WHERE alma_id=?;', (alma_id,))
    result = cursor.fetchone()
    close_connection(connection)
    return {
        'id': result[0],
        'name': result[1]
    }


# WEB FUNCTIONS

@app.route('/almas', methods=['GET'])
def web_get_all_almas():
    return jsonify({'alma\'s': get_all_almas()})


@app.route('/almas/<int:alma_id>', methods=['GET'])
def web_get_alma(alma_id):
    return jsonify(get_alma(alma_id))


if __name__ == '__main__':
    app.run(debug=True)
