# coding=utf-8

from lxml import html
from datetime import datetime, timedelta
from collections import OrderedDict
import requests
import sqlite3

# GENERAL VARIABLES

ALMA = {
    'Alma 1': 'alma_1',
    'Alma 2': 'alma_2',
    'Alma 3': 'alma_3',
    'Pauscollege': 'pauscollege',
    'Gasthuisberg': 'gasthuisberg'
}

DAYS_OF_THE_WEEK = OrderedDict(
    [
        ('Monday', 'maandag'),
        ('Tuesday', 'dinsdag'),
        ('Wednesday', 'woensdag'),
        ('Thursday', 'donderdag'),
        ('Friday', 'vrijdag')
    ]
)

COURSES = [
    'Soup',
    'Main Course'
]

DEFAULT_PRICING = {
    'Soup': '2.40'
}

# SCRAPER SPECIFIC VARIABLES

NA_IDENTIFIER = 'Niet beschikbaar'
VEGETARIAN_IDENTIFIER = 'Vegetarische schotel'

# DATE VARIABLES

DATE_TODAY = datetime.today()
DATE_TODAY_IN_WEEK = DATE_TODAY.weekday()

# DATABASE VARIABLES

DB_NAME = 'alma.db'
DB_CREATE_NAME = 'alma.sql'
DB_TABLES = [
    'ALMA',
    'OPTION',
    'MENU',
    'COURSE',
    'MENU_has_OPTION'
]


def get_week_menu(url):
    """
        1. Retrieves the HTML of an ALMA week menu page.
            1.1 Searches for the different day menus
            1.2 Searches for the different menu courses
            1.3 Searches for the different options in a course
        5. Returns a dictionary containing the different days and their menus
    """
    page = requests.get(url)
    tree = html.fromstring(page.text)

    menus = {}

    for day_name, day_identifier in DAYS_OF_THE_WEEK.iteritems():

        menu = {}
        menu_tree = tree.xpath('//a[@name="' + day_identifier + '"]/../following::table[1]')

        for course_count, course in enumerate(COURSES):

            options = {}
            is_vegetarian = []
            course_tree = menu_tree[0].xpath('child::tr[' + str(2 * (course_count + 1) + 1) + ']//td[last()]')

            for x in course_tree[0].xpath('br|img'):
                is_vegetarian.append(True) if x.xpath('@alt="' + VEGETARIAN_IDENTIFIER + '"') else is_vegetarian.append(False)

            for option_count, option in enumerate(course_tree[0].xpath('text()')):

                if option.strip():
                    name = option[:option.find(unicode('€', "utf-8"))].strip()
                    price_index = option.find(unicode('€', "utf-8"))

                    vegetarian = is_vegetarian[option_count] if option_count < len(is_vegetarian) else False

                    if name == NA_IDENTIFIER:
                        name = 'Not Available'
                        price = 'Not Available'
                    elif price_index < 0:
                        price = DEFAULT_PRICING[course].strip() if course in DEFAULT_PRICING else 'Not Available'
                    else:
                        price = option[price_index + 2:len(option)].strip()

                    options[option_count] = {
                        'name': name,
                        'price': price,
                        'vegetarian': vegetarian
                    }

            menu[course] = options

        menus[day_name] = menu

    return menus


# SQL FUNCTIONS


def drop_tables():
    for table_name in DB_TABLES:
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (table_name,))
        if cursor.fetchone() is not None:
            cursor.execute('DROP TABLE ' + table_name)


def create_tables():
    f = open(DB_CREATE_NAME, 'r')
    sql = f.read()
    cursor.executescript(sql)


def add_alma(alma_name):
    cursor.execute('SELECT alma_id FROM ALMA WHERE name=?;', (alma_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO ALMA (name) VALUES (?)', (alma_name,))
        return cursor.lastrowid
    else:
        return result[0]


def add_option(option_name, is_vegetarian):
    cursor.execute('SELECT option_id FROM OPTION WHERE name=?;', (option_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO OPTION (name,vegetarian) VALUES (?,?)', (option_name, is_vegetarian,))
        return cursor.lastrowid
    else:
        return result[0]


def add_course(course_name):
    cursor.execute('SELECT course_id FROM COURSE WHERE name=?;', (course_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO COURSE (name) VALUES (?)', (course_name,))
        return cursor.lastrowid
    else:
        return result[0]


def add_menu(alma_id, date):
    cursor.execute('SELECT menu_id FROM MENU WHERE alma_id=? AND date=?;', (alma_id, date,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO MENU (alma_id,date) VALUES (?,?)', (alma_id, date,))
        return cursor.lastrowid
    else:
        return result[0]


def add_option_to_menu(menu_id, course_id, option_id, price):
    cursor.execute('SELECT * FROM MENU_has_OPTION WHERE menu_id=? AND course_id=? AND option_id=?;', (menu_id, course_id, option_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO MENU_has_OPTION (menu_id, course_id, option_id, price) VALUES (?,?,?,?)', (menu_id, course_id, option_id, price,))
        return True
    else:
        return False


def save_week_menu(alma_id, week_menu):
    for day_count, day_name in enumerate(DAYS_OF_THE_WEEK.keys()):
        date = DATE_TODAY + timedelta(days=(day_count - DATE_TODAY_IN_WEEK) if DATE_TODAY_IN_WEEK < day_count else (day_count - DATE_TODAY_IN_WEEK))
        day_menu_id = add_menu(alma_id, date)
        for course_name in COURSES:
            course_id = add_course(course_name)
            for option_count in week_menu[day_name][course_name]:
                option = week_menu[day_name][course_name][option_count]
                option_id = add_option(option['name'], option['vegetarian'])
                add_option_to_menu(day_menu_id, course_id, option_id, option['price'])


connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

drop_tables()
create_tables()

for alma_name, alma_identifier in ALMA.iteritems():
    save_week_menu(add_alma(alma_name), get_week_menu('http://www.alma.be/' + alma_identifier + '/menu_dezeweek.php'))

connection.commit()
connection.close()
