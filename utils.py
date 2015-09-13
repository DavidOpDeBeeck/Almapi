import sqlite3

# DB STATIC VARIABLES

DB_NAME = 'alma.db'
DB_CREATE_NAME = 'alma.sql'
DB_TABLES = [
    'ALMA',
    'OPTION',
    'MENU',
    'COURSE',
    'MENU_has_OPTION'
]

# CONNECTION

connection = None

# DB FUNCTIONS

def open_connection():
    global connection
    connection = sqlite3.connect(DB_NAME)
    return connection.cursor()


def close_connection():
    connection.commit()
    connection.close()


def drop_tables():
    try:
        cursor = open_connection()
        for table_name in DB_TABLES:
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (table_name,))
            if cursor.fetchone() is not None:
                cursor.execute('DROP TABLE ' + table_name)
    finally:
        close_connection()


def create_tables():
    try:
        cursor = open_connection()
        f = open(DB_CREATE_NAME, 'r')
        sql = f.read()
        cursor.executescript(sql)
    finally:
        close_connection()


def get_all_almas():
    try:
        cursor = open_connection()
        cursor.execute('SELECT alma_id,name FROM ALMA;')
        response = []
        for alma_index, alma_name in cursor.fetchall():
            response.append({
                'id': alma_index,
                'name': alma_name
            })
        return response
    finally:
        close_connection()


def get_alma(alma_id):
    try:
        cursor = open_connection()
        cursor.execute('SELECT alma_id,name FROM ALMA WHERE alma_id=?;', (alma_id,))
        result = cursor.fetchone()
        return {
            'id': result[0],
            'name': result[1]
        }
    finally:
        close_connection()


def get_menu(alma_id):
    try:
        cursor = open_connection()

        response = {}
        courses = {}

        cursor.execute('SELECT menu_id,date FROM MENU WHERE alma_id=?;', (alma_id,))
        menus = cursor.fetchall()
        for menu in menus:
            date = menu[1][:menu[1].find(' ')].strip()
            response[date] = {}

            cursor.execute('SELECT course_id,name FROM COURSE;')
            result = cursor.fetchall()

            for course in result:
                courses[course[0]] = course[1]
                response[date][course[1]] = []

            cursor.execute('SELECT option_id,course_id,price FROM MENU_has_OPTION WHERE menu_id=?;', (menu[0],))
            options = cursor.fetchall()
            for option in options:
                cursor.execute('SELECT option_id,name,vegetarian FROM OPTION WHERE option_id=?;', (option[0],))
                for option_info in cursor.fetchall():
                    response[date][courses[option[1]]].append({
                        'name': option_info[1],
                        'price': option[2],
                        'vegetarian': option_info[2]
                    })
        return response
    finally:
        close_connection()


def add_alma(alma_name):
    try:
        cursor = open_connection()
        cursor.execute('SELECT alma_id FROM ALMA WHERE name=?;', (alma_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO ALMA (name) VALUES (?)', (alma_name,))
            return cursor.lastrowid
        else:
            return result[0]
    finally:
        close_connection()


def add_option(option_name, is_vegetarian):
    try:
        cursor = open_connection()
        cursor.execute('SELECT option_id FROM OPTION WHERE name=?;', (option_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO OPTION (name,vegetarian) VALUES (?,?)', (option_name, is_vegetarian,))
            return cursor.lastrowid
        else:
            return result[0]
    finally:
        close_connection()


def add_course(course_name):
    try:
        cursor = open_connection()
        cursor.execute('SELECT course_id FROM COURSE WHERE name=?;', (course_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO COURSE (name) VALUES (?)', (course_name,))
            return cursor.lastrowid
        else:
            return result[0]
    finally:
        close_connection()


def add_menu(alma_id, date):
    try:
        cursor = open_connection()
        cursor.execute('SELECT menu_id FROM MENU WHERE alma_id=? AND date=?;', (alma_id, date,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO MENU (alma_id,date) VALUES (?,?)', (alma_id, date,))
            return cursor.lastrowid
        else:
            return result[0]
    finally:
        close_connection()


def add_option_to_menu(menu_id, course_id, option_id, price):
    try:
        cursor = open_connection()
        cursor.execute('SELECT option_id FROM MENU_has_OPTION WHERE menu_id=? AND course_id=? AND option_id=?;', (menu_id, course_id, option_id,))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO MENU_has_OPTION (menu_id, course_id, option_id, price) VALUES (?,?,?,?)', (menu_id, course_id, option_id, price,))
        return option_id
    finally:
        close_connection()
