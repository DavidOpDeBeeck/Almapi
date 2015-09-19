import sqlite3
from datetime import datetime, timedelta, date

# DB STATIC VARIABLES

DB_NAME = 'database/alma.db'
DB_CREATE_NAME = 'database/alma.sql'
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
    """
        Opens the connection to the database file.
        :return The cursor of the connection.
    """
    global connection
    connection = sqlite3.connect(DB_NAME)
    return connection.cursor()

def close_connection():
    """
        Closes the connection to the database file.
    """
    global connection
    connection.commit()
    connection.close()

def create_tables():
    """
        Checks if the tables in array DB_TABLES exist.
        If they don't exist it executes the create tables script in DB_CREATE_NAME.
    """
    if not check_if_tables_exist():
        try:
            cursor = open_connection()
            f = open(DB_CREATE_NAME, 'r')
            sql = f.read()
            cursor.executescript(sql)
        finally:
            close_connection()

def drop_tables():
    """
        Checks if the tables in array DB_TABLES exist.
        If they do exist it executes the drop table command.
    """
    try:
        cursor = open_connection()
        for table_name in DB_TABLES:
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (table_name,))
            if cursor.fetchone() is not None:
                cursor.execute('DROP TABLE ' + table_name)
    finally:
        close_connection()

def check_if_tables_exist():
    """
        Checks if the tables in array DB_TABLES exist.
        :return True if they all exist. False if one of them doesn't exist.
    """
    try:
        cursor = open_connection()
        exist = True
        for table_name in DB_TABLES:
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (table_name,))
            if cursor.fetchone() is None:
                exist = False
        return exist
    finally:
        close_connection()

def get_all_almas():
    """
        :return A list containing the id and name of each alma.
    """
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
    """
        :param alma_id The id of the alma whose information you want to retrieve.
        :type alma_id Integer
        :return A dictionary containing the id and name of the alma with the specified id.
    """
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

def get_menu(alma_id, year, week):
    """
        :param alma_id The id of the alma whose menu you want to retrieve.
        :type alma_id Integer
        :param year The year in which the menu you want to retrieve is.
        :type year Integer
        :param week The week in which the menu you want to retrieve is.
        :type week Integer
        :return A dictionary containing the different days and their menus for the alma with the specified id.
    """
    try:
        cursor = open_connection()

        from_date = get_first_day_in_week(year, week)
        to_date = from_date + timedelta(days=6)

        response = []
        courses = {}

        cursor.execute('SELECT course_id,name FROM COURSE;')

        for course in cursor.fetchall():
            courses[course[0]] = course[1]

        cursor.execute('SELECT menu_id,date FROM MENU WHERE alma_id=? AND date > ? AND date < ?;', (alma_id, from_date, to_date,))
        menus = cursor.fetchall()
        for menu in menus:
            day = {
                'menu': {},
                'date': menu[1][:menu[1].find(' ')].strip()
            }

            for course_name in courses.values():
                day['menu'][course_name] = []

            cursor.execute('SELECT option_id,course_id,price FROM MENU_has_OPTION WHERE menu_id=?;', (menu[0],))
            options = cursor.fetchall()
            for option in options:
                cursor.execute('SELECT option_id,name,vegetarian FROM OPTION WHERE option_id=?;', (option[0],))
                for option_info in cursor.fetchall():
                    day['menu'][courses[option[1]]].append({
                        'name': option_info[1],
                        'price': option[2],
                        'vegetarian': option_info[2]
                    })
            response.append(day)
        return response
    finally:
        close_connection()

def add_alma(alma_name):
    """
        :param alma_name The name of the alma to be added.
        :type alma_name String
        :return The id of the alma with the specified name.
    """
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
    """
        :param option_name The name of the option to be added.
        :type option_name String
        :param is_vegetarian If the option is vegetarian.
        :type is_vegetarian Boolean
        :return The id of the option with the specified name.
    """
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
    """
        :param course_name The name of the course to be added.
        :type course_name String
        :return The id of the course with the specified name.
    """
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

def add_menu(alma_id, menu_date):
    """
        :param alma_id The id of the alma to be added.
        :type alma_id Integer
        :param menu_date The date of the menu to be added.
        :type menu_date Date
        :return The id of the menu with the specified alma and date.
    """
    try:
        cursor = open_connection()
        cursor.execute('SELECT menu_id FROM MENU WHERE alma_id=? AND date=?;', (alma_id, menu_date,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO MENU (alma_id,date) VALUES (?,?)', (alma_id, menu_date,))
            return cursor.lastrowid
        else:
            return result[0]
    finally:
        close_connection()

def add_options_to_menu(menu_id, course_id, options, prices):
    """
        :param menu_id The id of the menu.
        :type menu_id Integer
        :param course_id The id of the course.
        :type course_id Integer
        :param options The id of the options to be added to the menu and course.
        :type options Array of Integers
        :param prices The prices of the options to be added to the menu and course.
        :type prices Array of Integers
        :return The id of the options.
    """
    try:
        cursor = open_connection()
        cursor.execute(' DELETE FROM MENU_has_OPTION WHERE menu_id=? AND course_id=?;', (menu_id, course_id,))
        for option_index, option_id in enumerate(options):
            cursor.execute('INSERT INTO MENU_has_OPTION (menu_id, course_id, option_id, price) VALUES (?,?,?,?)', (menu_id, course_id, option_id, prices[option_index],))
        return options
    finally:
        close_connection()

# HELPER FUNCTIONS

def get_first_day_in_week(year, week):
    """
        :param year The year the week is in.
        :type year Integer
        :param week The week you want the first day of.
        :type week Integer
        :return The first day in the specified week and year.
    """
    ret = datetime.strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
    if date(year, 1, 4).isoweekday() > 4:
        ret -= timedelta(days=7)
    return ret
