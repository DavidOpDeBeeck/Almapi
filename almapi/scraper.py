# coding=utf-8
import sys
import requests
import utilities
from lxml import html
from datetime import datetime, timedelta

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
    'Thursday',
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

# SCRAPER

def get_week_menu(url, day_identifier):
    """
        :param url The url that contains the menu
        :type url String
        :param day_identifier Identifier array used to identify the day elements on the page
        :type day_identifier Array of strings

        Retrieves the HTML of an ALMA week menu page.
            Searches for the different day menus
                Searches for the different menu courses
                    Searches for the different options in a course

        :return A dictionary containing the different days and their menus
    """
    page = requests.get(url)
    tree = html.fromstring(page.text)

    week_menus = {}

    for day_index, day_name in enumerate(DAYS_OF_THE_WEEK):
        day_menu = {}
        day_menu_tree = tree.xpath('//a[@name="' + day_identifier[day_index] + '"]/../following::table[1]')

        for course_index, course_name in enumerate(COURSES):
            course_options = {}
            vegetarian_list = []
            course_tree = day_menu_tree[0].xpath('child::tr[' + str(2 * (course_index + 1) + 1) + ']//td[last()]')

            for x in course_tree[0].xpath('br|img'):
                vegetarian_list.append(True) if x.xpath('@alt="' + VEGETARIAN_IDENTIFIER + '"') else vegetarian_list.append(False)

            for option_index, option_element_text in enumerate(course_tree[0].xpath('text()')):
                if option_element_text.strip():
                    option_name = option_element_text[:option_element_text.find(unicode('€', "utf-8"))].strip()
                    option_price_index = option_element_text.find(unicode('€', "utf-8"))
                    option_is_vegetarian = vegetarian_list[option_index] if option_index < len(vegetarian_list) else False

                    if option_name == NA_IDENTIFIER:
                        option_name = option_price = 'Not Available'
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

def save_week_menu(alma_id, week_menu, day_modifier):
    """
        :param alma_id The id of the current alma
        :type alma_id Integer
        :param week_menu The menu of the current alma
        :type week_menu Dictionary #get_week_menu
        :param day_modifier The modifier used to calculate the day of the menu (day_index - DATE_TODAY_IN_WEEK + day_modifier)
        :type day_modifier Integer

        Iterates over all the days of the week.
            For each day we calculate the date (:see day_modifier) and add it to the database. (Returns a menu id)
                Iterates over all the possible courses and adds them to the database. (Returns a course id)
                    Iterates over all the options in a course of the current day and adds them to the database.
    """
    for day_index, day_name in enumerate(DAYS_OF_THE_WEEK):
        date = DATE_TODAY + timedelta(days=(day_index - DATE_TODAY_IN_WEEK + day_modifier))
        day_menu_id = utilities.add_menu(alma_id, date.date())
        for course_name in COURSES:
            options = []
            options_price = []
            course_id = utilities.add_course(course_name)
            for option_count in week_menu[day_name][course_name]:
                option = week_menu[day_name][course_name][option_count]
                options.append(utilities.add_option(option['name'], option['vegetarian']))
                options_price.append(option['price'])
            utilities.add_options_to_menu(day_menu_id, course_id, options, options_price)

# IF CLEAN IS ADDED AS AN ARGUMENT WE DROP THE CURRENT DATABASE
if "clean" in sys.argv:
    utilities.drop_tables()

# CREATES THE TABLES IF THEY DON'T EXIST
utilities.create_tables()

# ITERATES OVER ALL THE ALMA'S AND ADDS THE CURRENT AND NEXT WEEK TO THE DATABASE
for alma_name, alma_identifier in ALMA.items():
    save_week_menu(utilities.add_alma(alma_name), get_week_menu('http://www.alma.be/%s/menu_dezeweek.php' % alma_identifier, DAY_IDENTIFIER[0]), 0)
    save_week_menu(utilities.add_alma(alma_name), get_week_menu('http://www.alma.be/%s/menu_volgweek.php' % alma_identifier, DAY_IDENTIFIER[1]), 7)
