# coding=utf-8

from lxml import html
from datetime import datetime, timedelta
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

DAYS_OF_THE_WEEK = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Friday'
]

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
DAY_IDENTIFIER = [
    [
        'maandag',
        'dinsdag',
        'woensdag',
        'donderdag',
        'vrijdag'
    ],
    [
        'maandag2',
        'dinsdag2',
        'woensdag2',
        'donderdag2',
        'vrijdag2'
    ]
]

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

# SCRAPER

def get_week_menu(url, day_identifier):
    """
        1. Retrieves the HTML of an ALMA week menu page.
            1.1 Searches for the different day menus
                1.1.1 Searches for the different menu courses
                    1.1.1.1 Searches for the different options in a course
        2. Returns a dictionary containing the different days and their menus
    """
    page = requests.get(url)
    tree = html.fromstring(page.text)

    week_menus = {}

    for day_index, day_name in enumerate(DAYS_OF_THE_WEEK):

        day_menu = {}
        day_menu_tree = tree.xpath('//a[@name="' + day_identifier[day_index] + '"]/../following::table[1]')

        for course_index, course_name in enumerate(COURSES):

            course_options = {}
            is_option_vegetarian_list = []
            course_tree = day_menu_tree[0].xpath('child::tr[' + str(2 * (course_index + 1) + 1) + ']//td[last()]')

            for x in course_tree[0].xpath('br|img'):
                is_option_vegetarian_list.append(True) if x.xpath('@alt="' + VEGETARIAN_IDENTIFIER + '"') else is_option_vegetarian_list.append(False)

            for option_index, option_element_text in enumerate(course_tree[0].xpath('text()')):

                if option_element_text.strip():
                    option_name = option_element_text[:option_element_text.find(unicode('€', "utf-8"))].strip()
                    option_price_index = option_element_text.find(unicode('€', "utf-8"))

                    option_is_vegetarian = is_option_vegetarian_list[option_index] if option_index < len(is_option_vegetarian_list) else False

                    if option_name == NA_IDENTIFIER:
                        option_name = 'Not Available'
                        option_price = 'Not Available'
                    elif option_price_index < 0:
                        option_price = DEFAULT_PRICING[course_name].strip() if course_name in DEFAULT_PRICING else 'Not Available'
                    else:
                        option_price = option_element_text[option_price_index + 2:len(option_element_text)].strip()

                    course_options[option_index] = {
                        'name': option_name,
                        'price': option_price,
                        'vegetarian': option_is_vegetarian
                    }

            day_menu[course_name] = course_options

        week_menus[day_name] = day_menu

    return week_menus


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


def add_or_get_alma(alma_name):
    cursor.execute('SELECT alma_id FROM ALMA WHERE name=?;', (alma_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO ALMA (name) VALUES (?)', (alma_name,))
        return cursor.lastrowid
    else:
        return result[0]


def add_or_get_option(option_name, is_vegetarian):
    cursor.execute('SELECT option_id FROM OPTION WHERE name=?;', (option_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO OPTION (name,vegetarian) VALUES (?,?)', (option_name, is_vegetarian,))
        return cursor.lastrowid
    else:
        return result[0]


def add_or_get_course(course_name):
    cursor.execute('SELECT course_id FROM COURSE WHERE name=?;', (course_name,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('INSERT INTO COURSE (name) VALUES (?)', (course_name,))
        return cursor.lastrowid
    else:
        return result[0]


def add_or_get_menu(alma_id, date):
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


def save_week_menu(alma_id, week_menu, day_modifier):
    for day_index, day_name in enumerate(DAYS_OF_THE_WEEK):
        date = DATE_TODAY + timedelta(days=(day_index - DATE_TODAY_IN_WEEK + day_modifier))
        day_menu_id = add_or_get_menu(alma_id, date)
        for course_name in COURSES:
            course_id = add_or_get_course(course_name)
            for option_count in week_menu[day_name][course_name]:
                option = week_menu[day_name][course_name][option_count]
                option_id = add_or_get_option(option['name'], option['vegetarian'])
                add_option_to_menu(day_menu_id, course_id, option_id, option['price'])

# SCRIPT

connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

drop_tables()
create_tables()

for alma_name, alma_identifier in ALMA.iteritems():
    save_week_menu(add_or_get_alma(alma_name), get_week_menu('http://www.alma.be/%s/menu_dezeweek.php' % alma_identifier, DAY_IDENTIFIER[0]), 0)
    save_week_menu(add_or_get_alma(alma_name), get_week_menu('http://www.alma.be/%s/menu_volgweek.php' % alma_identifier, DAY_IDENTIFIER[1]), 7)

connection.commit()
connection.close()