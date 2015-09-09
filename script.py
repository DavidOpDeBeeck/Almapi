# coding=utf-8

from lxml import html
from datetime import datetime, timedelta
from collections import OrderedDict
import requests
import sqlite3

DAYS_OF_THE_WEEK = OrderedDict()
DAYS_OF_THE_WEEK['Monday'] = 'maandag'
DAYS_OF_THE_WEEK['Tuesday'] = 'dinsdag'
DAYS_OF_THE_WEEK['Wednesday'] = 'woensdag'
DAYS_OF_THE_WEEK['Thursday'] = 'donderdag'
DAYS_OF_THE_WEEK['Friday'] = 'vrijdag'

COURSES = [
    'Soup',
    'Main Course'
]

DEFAULT_PRICING = {
    'Soup': '2.40'
}

NA_IDENTIFIER = 'Niet beschikbaar'
VEGETARIAN_IDENTIFIER = 'Vegetarische schotel'

ALMA = {
    'Alma 1': 'alma_1',
    'Alma 2': 'alma_2',
    'Alma 3': 'alma_3',
    'Pauscollege': 'pauscollege',
    'Gasthuisberg': 'gasthuisberg'
}


def get_week_menu(url):
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

DB_NAME = 'alma.db'
DB_TABLES = [
    'ALMA',
    'OPTION',
    'MENU',
    'COURSE',
    'MENU_has_OPTION'
]


def drop_tables():
    for table_name in DB_TABLES:
        param = (table_name,)
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', param)
        if cursor.fetchone() is not None:
            cursor.execute('DROP TABLE ' + table_name)
    connection.commit()


def create_tables():
    f = open('alma.sql', 'r')
    sql = f.read()
    cursor.executescript(sql)
    connection.commit()


def add_alma(alma_name):
    args = (alma_name,)
    cursor.execute('SELECT alma_id FROM ALMA WHERE name=?;', args)
    alma = cursor.fetchone()
    if alma is None:
        args = (alma_name,)
        cursor.execute('INSERT INTO ALMA (name) VALUES (?)', args)
        return cursor.lastrowid
    else:
        return alma[0]


def add_option(option_name, is_vegetarian):
    args = (option_name,)
    cursor.execute('SELECT option_id FROM OPTION WHERE name=?;', args)
    option = cursor.fetchone()
    if option is None:
        args = (option_name, is_vegetarian,)
        cursor.execute('INSERT INTO OPTION (name,vegetarian) VALUES (?,?)', args)
        return cursor.lastrowid
    else:
        return option[0]


def add_course(course_name):
    args = (course_name,)
    cursor.execute('SELECT course_id FROM COURSE WHERE name=?;', args)
    crs = cursor.fetchone()
    if crs is None:
        args = (course_name,)
        cursor.execute('INSERT INTO COURSE (name) VALUES (?)', args)
        return cursor.lastrowid
    else:
        return crs[0]


def add_menu(alma_id, date):
    args = (alma_id, date,)
    cursor.execute('SELECT menu_id FROM MENU WHERE alma_id=? AND date=?;', args)
    menu = cursor.fetchone()
    if menu is None:
        args = (alma_id, date,)
        cursor.execute('INSERT INTO MENU (alma_id,date) VALUES (?,?)', args)
        return cursor.lastrowid
    else:
        return menu[0]


def add_option_to_menu(menu_id, course_id, option_id, price):
    args = (menu_id, course_id, option_id,)
    cursor.execute('SELECT * FROM MENU_has_OPTION WHERE menu_id=? AND course_id=? AND option_id=?;', args)
    menu_option = cursor.fetchone()
    if menu_option is None:
        args = (menu_id, course_id, option_id, price,)
        cursor.execute('INSERT INTO MENU_has_OPTION (menu_id, course_id, option_id, price) VALUES (?,?,?,?)', args)
        return True
    else:
        return False

# SCRIPT

connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

drop_tables()
create_tables()

date_today = datetime.today()
date_today_in_week = date_today.weekday()

for key, value in ALMA.iteritems():
    alma_id = add_alma(key)
    week_menu = get_week_menu('http://www.alma.be/' + value + '/menu_dezeweek.php')
    for day_count, day_name in enumerate(DAYS_OF_THE_WEEK.keys()):
        date = date_today + timedelta(days=(day_count - date_today_in_week) if date_today_in_week < day_count else (day_count - date_today_in_week))
        day_menu_id = add_menu(alma_id, date)
        for course_name in COURSES:
            course_id = add_course(course_name)
            for option_count in week_menu[day_name][course_name]:
                option = week_menu[day_name][course_name][option_count]
                option_id = add_option(option['name'], option['vegetarian'])
                add_option_to_menu(day_menu_id, course_id, option_id, option['price'])

connection.commit()
connection.close()
