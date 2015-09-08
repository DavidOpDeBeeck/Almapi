# coding=utf-8

from lxml import html
import requests

DAYS_OF_THE_WEEK = {
    'Monday': 'maandag',
    'Tuesday': 'dinsdag',
    'Wednesday': 'woensdag',
    'Thursday': 'donderdag',
    'Friday': 'vrijdag'
}

COURSES = [
    'Soup',
    'Main Course'
]

DEFAULT_PRICING = {
    'Soup': '2.40'
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
            course_tree = menu_tree[0].xpath('child::tr[' + str(2 * (course_count + 1) + 1) + ']//td[last()]/text()')

            for option_count, option in enumerate(course_tree):

                if option.strip():
                    name = option[:option.find(unicode('€', "utf-8"))].strip()
                    price_index = option.find(unicode('€', "utf-8"))

                    if name == 'Niet beschikbaar':
                        name = 'Not Available'
                        price = 'Not Available'
                    elif price_index < 0:
                        price = DEFAULT_PRICING[course].strip() if course in DEFAULT_PRICING else 'Not Available'
                    else:
                        price = option[price_index + 2:len(option)].strip()

                    options[option_count] = {
                        'name': name,
                        'price': price
                    }

            menu[course] = options

        menus[day_name] = menu

    return menus


def print_week_menu(week_menu):
    for menu in week_menu:
        print menu
        for course in COURSES:
            print "  " + course
            for option in week_menu[menu][course]:
                print "      name : " + week_menu[menu][course][option]['name']
                print "      price : " + week_menu[menu][course][option]['price']


ALMA = {
    'Alma 1': 'alma_1',
    'Alma 2': 'alma_2',
    'Alma 3': 'alma_3',
    'Pauscollege': 'pauscollege',
    'Gasthuisberg': 'gasthuisberg'
}

for key, value in ALMA.iteritems():
    print "------------------"
    print key
    print "------------------"
    print_week_menu(get_week_menu('http://www.alma.be/' + value + '/menu_dezeweek.php'))
