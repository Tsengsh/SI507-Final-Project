#############################
###     Final Project     ###
### Name: Hsiao-Han Tseng ###      
### Unique Name: tsengsh  ###            
#############################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import time
from selenium import webdriver

headers = {
    'User-Agent': 'UMSI 507 Course Project - Python Scraping',
    'From': 'tsengsh@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

CACHE_DICT = {}
CACHE_FILE_NAME = 'table_cache.json'

# Cache
def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

CACHE_DICT = load_cache()

#####################################
####  PART ZERO: STATES ABBREV.  ####
#####################################
# MAKE THE SOUP FOR STATE LIST
STATE_ABBREV_FULL_DICT = {}
STATE_LIST_TAG = "tr"
STATE_NAME_TAG = "td"

STATE_LIST_BASEURL = "https://www.50states.com/abbreviations.htm"
STATE_LIST = make_url_request_using_cache(STATE_LIST_BASEURL, CACHE_DICT)
STATE_LIST_SOUP = BeautifulSoup(STATE_LIST, "html.parser")
STATE_LIST_CONTENT = STATE_LIST_SOUP.find_all(STATE_LIST_TAG)
for i in STATE_LIST_CONTENT:
    try: 
        STATE_NAME = i.find_all(STATE_NAME_TAG)[0].text.replace(" ", "_").lower()  # STATE_NAME
        STATE_ABBREV = i.find_all(STATE_NAME_TAG)[1].text  # STATE_ABBREV
        STATE_ABBREV_FULL_DICT[STATE_ABBREV] = STATE_NAME
    except:
        pass

###############################
####  PART ONE: UX SCHOOL  ####
###############################
# CREATE DICTIONARY
UX_PROGRAM_DICT = {}
'''
UX_SCHOOL_DICT[SCHOOL_INDEX] = [UNIVERSITY, 
PROGRAM, CITY_NAME, STATE_ABBREV, CITY_NAME]
'''

UX_SCHOOL_BASEURL = "https://uxmastery.com/resources/ux-degrees/"
CONTENT_TAG = "tbody"
CONTENT_CLASS = "row-hover"
COLUMN_TAG = "td"
COUNTRY_CLASS = "column-1"
CITY_CLASS = "column-2"
UNIVERSITY_CLASS = "column-3"
PROGRAM_CLASS = "column-4"
PROGRAM_LINK_TAG = "td"
PROGRAM_LINK_CLASS = "column-3"
PROGRAM_LINK_A_TAG = "a"
PROGRAM_LINK_HREF_TAG = "href"


# MAKE THE SOUP FOR TOP UX SCHOOL
UX_SCHOOL_CONTENT = make_url_request_using_cache(UX_SCHOOL_BASEURL, CACHE_DICT)
UX_SCHOOL_SOUP = BeautifulSoup(UX_SCHOOL_CONTENT, "html.parser")
CONTENT = UX_SCHOOL_SOUP.find(CONTENT_TAG, class_=CONTENT_CLASS)
COMBINE_LIST = []
STATE_WITH_SCHOOL_LIST = []
CITY_WITH_SCHOOL_LIST = []

# FOR EACH SCHOOL IN THE US LISTED
for i in CONTENT:

    # EXTRACT COUNTTRY NAME
    COUNTRY = i.find(COLUMN_TAG, class_=COUNTRY_CLASS).text
    if COUNTRY == "USA":
        # EXTRACT CITY NAME
        CITY = i.find(COLUMN_TAG, class_=CITY_CLASS).text.split(",")[0]
        # if CITY not in CITY_WITH_SCHOOL_LIST:
        CITY_WITH_SCHOOL_LIST.append(CITY.replace(" ", "_").replace("Milwakee", "Milwaukee").lower().replace("multiple_campuses", "chicago").replace("piscatawny", "piscataway"))
        CITY_KEY = CITY.replace(" ", "_").replace("Milwakee", "Milwaukee").lower().replace("multiple_campuses", "chicago").replace("piscatawny", "piscataway")
        # EXTRACT STATE NAME
        try:
            STATE = i.find(COLUMN_TAG, class_=CITY_CLASS).text.split(",")[1].strip()
            # if STATE not in STATE_WITH_SCHOOL_LIST: 
        except:
            if CITY == "East Lansing":
                STATE = "MI"
            elif CITY == "Multiple Campuses":
                STATE = "IL"
        STATE_WITH_SCHOOL_LIST.append(STATE)
        CITY = CITY_KEY.replace("_", " ").capitalize()
        # EXTRACT UNIVERSITY
        UNIVERSITY = i.find(COLUMN_TAG, class_=UNIVERSITY_CLASS).text

        # EXTRACT PROGRAM
        PROGRAM = i.find(COLUMN_TAG, class_=PROGRAM_CLASS).text.replace("[","").replace("]","")

        # EXTRACCT PROGRAM LINK
        PROGRAM_LINK = i.find(PROGRAM_LINK_TAG, class_=PROGRAM_LINK_CLASS).find(PROGRAM_LINK_A_TAG)[PROGRAM_LINK_HREF_TAG]

        # CREATE PROGRAM TYPE
        PROGRAM_TYPE = None
        if PROGRAM[0] == "B" or PROGRAM[0] == "U" or PROGRAM[0] == "I":
            PROGRAM_TYPE = "bachelor"
        elif PROGRAM[0] == "M" or PROGRAM[0] == "T" or PROGRAM[0] == "P":
            PROGRAM_TYPE = "masterorphd"
        elif PROGRAM[0] == "C" or PROGRAM[0] == "D" or PROGRAM[0] == "H":
            PROGRAM_TYPE = "certificates"

        #### CREATE SCHOOL DICTIONARY
        
        UX_PROGRAM_DICT[PROGRAM] = [PROGRAM, UNIVERSITY, CITY_KEY, PROGRAM_LINK, PROGRAM_TYPE]


#####################################
####  PART TWO: CITY OF SCHOOLS  ####
#####################################

# CREATE DICTIONARY
CITY_DICT = {}
'''
CITY_DICT[STATE_WITH_SCHOOL_DICT.keys()] = [CITY_NAME, 
STATE_NAME, POPULATION, MEDIAN_INCOME, MEDIAN_AGE, 
CLIMATE_COMFORT_INDEX, UNEMPLOYMENT_RATE, MEDIAN_HOME_PRICE]
'''

# CREATE URL FOR RESTRICTED SEARCH
BASE_URL = "https://www.bestplaces.net/find/"
BASE_STATE_CITY_URL = "https://www.bestplaces.net/city/"
DETAILS_TAG = "div"
DETAILS_CLASS = "col-md-3 px-1"

POPULATION_TAG = "p"
POPULATION_CLASS = "text-center py-0 my-0"
UNEMPLOYMENT_TAG = "p"
UNEMPLOYMENT_CLASS = "text-center"
UNEMPLOYMENT_STYLE = "font-size:33px;"
MEDIAN_INCOME_TAG = "p"
MEDIAN_INCOME_CLASS = "text-center"
MEDIAN_INCOME_STYLE = "font-size:33px;"
AGE_COMFORT_TAG = "p"
AGE_COMFORT_CLASS = "text-center"
AGE_COMFORT_STYLE = "font-size:33px;"

for i in range(51):
    STATE_FULL_NAME = STATE_ABBREV_FULL_DICT[STATE_WITH_SCHOOL_LIST[i]]
    URL = BASE_STATE_CITY_URL+STATE_FULL_NAME + "/" + CITY_WITH_SCHOOL_LIST[i]

    # MAKE THE SOUP FOR CITY LIST
    CITY_CONTENT = make_url_request_using_cache(URL, CACHE_DICT)
    CITY_CONTENT_SOUP = BeautifulSoup(CITY_CONTENT, "html.parser")
    DETAIL_PART = CITY_CONTENT_SOUP.find_all(DETAILS_TAG, class_=DETAILS_CLASS)

    # EXTRACT POPULATION
    POPULATION = DETAIL_PART[0].find(POPULATION_TAG, class_=POPULATION_CLASS).text.strip().replace(" ","").replace(",", "")

    #EXTRACT UNEMPLOYMENT RATE
    UNEMPLOYMENT_RATE = DETAIL_PART[0].find(UNEMPLOYMENT_TAG, class_=UNEMPLOYMENT_CLASS, style=UNEMPLOYMENT_STYLE).text[:-1].strip()

    # MEDIAN INCOME AND MEDIAN HOME PRICE
    MEDIAN_INCOME_HOME = DETAIL_PART[1].find_all(MEDIAN_INCOME_TAG, class_=MEDIAN_INCOME_CLASS, style=MEDIAN_INCOME_STYLE)
    # EXTRACT MEDIAN INCOME
    MEDIAN_INCOME = MEDIAN_INCOME_HOME[0].text[1:].strip().replace(" ", "").replace(",", "")
    # EXTRACT MEDIAN HOME PRICE
    MEDIAN_HOME_PRICE = MEDIAN_INCOME_HOME[1].text[1:]

    # MEDIAN AGE AND CONFORT INDEX
    AGE_COMFORT_INDEX = DETAIL_PART[2].find_all(AGE_COMFORT_TAG, class_=AGE_COMFORT_CLASS, style=AGE_COMFORT_STYLE)
    # EXTRACT MEDIAN AGE
    AGE = AGE_COMFORT_INDEX[0].text
    # EXTRACT COMFORT INDEX
    COMFORT_INDEX = AGE_COMFORT_INDEX[1].text[:-3]

    # CREATE CITY NAME
    CITYID = CITY_WITH_SCHOOL_LIST[i]
    CITY_NAME = CITY_WITH_SCHOOL_LIST[i].replace("_", " ").capitalize()

    #### CREATE CITY DICTIONARY
    CITY_DICT[CITY_WITH_SCHOOL_LIST[i]] = [CITY_NAME, STATE_FULL_NAME.replace("_", " ").capitalize(), POPULATION, UNEMPLOYMENT_RATE, MEDIAN_INCOME, MEDIAN_HOME_PRICE, AGE, COMFORT_INDEX, CITY_WITH_SCHOOL_LIST[i]]

###################################
####  PART THREE: IMPORT DATA  ####
###################################
conn = sqlite3.connect("ux.sqlite")
cur = conn.cursor()

drop_program_sql = 'DROP TABLE IF EXISTS "Programs"'
drop_city_sql = 'DROP TABLE IF EXISTS "Cities"'

program_table = '''
    CREATE TABLE IF NOT EXISTS 'Programs'(
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT, 
        'Program' TEXT NOT NULL,
        'University' TEXT NOT NULL, 
        'CityId' INTEGER,
        'ProgramLink' TEXT NOT NULL,
        'ProgramType' TEXT NOT NULL
    )
'''

city_table = '''
    CREATE TABLE IF NOT EXISTS 'Cities'(
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'CityName' TEXT NOT NULL,
        'StateName' TEXT NOT NULL,
        'Population' INTEGER NOT NULL,
        'UnemploymentRate' REAL NOT NULL,
        'MedianIncome' INTEGER NOT NULL,
        'MedianHomePrice' INTEGER NOT NULL,
        'Age' REAL NOT NULL,
        'ComfortIndex' REAL NOT NULL,  
        'CityKey' TEXT NOT NULL 
    )

'''

cur.execute(drop_program_sql)
cur.execute(drop_city_sql)
cur.execute(program_table)
cur.execute(city_table)
conn.commit()

import_program = '''
    INSERT INTO Programs
    VALUES (NULL,?,?,?,?,?)
'''

import_city =  '''
    INSERT INTO Cities
    VALUES (NULL,?,?,?,?,?,?,?,?,?)
'''
for city in CITY_DICT:
    cur.execute(import_city, CITY_DICT[city])

connect_tables = '''
    SELECT Id FROM Cities
    WHERE CityKey = ?
'''

for program in UX_PROGRAM_DICT:
    cur.execute(connect_tables, [UX_PROGRAM_DICT[program][2]])
    res = cur.fetchone()
    city_id = None
    if res is not None:
        city_id = res[0]

    cur.execute(import_program, [
        UX_PROGRAM_DICT[program][0],
        UX_PROGRAM_DICT[program][1],
        city_id,
        UX_PROGRAM_DICT[program][3],
        UX_PROGRAM_DICT[program][4]]
        )

conn.commit()
conn.close()

###############################################
####  ORIGINAL CRAWLING AND SCRAPING CODE  ####
###############################################
'''
ALL_BASEURL = "https://www.bestplaces.net/"
STATE_BASEURL = "https://www.bestplaces.net/find/state.aspx?state="
CITY_BASEURL = "https://www.bestplaces.net/find/"
STATE_TAG = "div"
CITY_TAG = "div"
CITY_CLASS = "col-md-4"
CITY_URL_TAG = "a"
HREF_TAG = "href"
# DICTIONARY
CITY_DICT = {}
'''

'''
# CREATE STATE URL
CITY_NAME_LIST = []
for i in STATE_WITH_SCHOOL_DICT:
    STATE_URL = STATE_BASEURL + i.lower()
    # MAKE THE SOUP FOR STATE LIST
    STATE_LIST_CONTENT = make_url_request_using_cache(STATE_URL, CACHE_DICT)
    STATE_LIST_SOUP = BeautifulSoup(STATE_LIST_CONTENT, "html.parser")
    CITY_PART = STATE_LIST_SOUP.find_all(CITY_TAG, class_=CITY_CLASS)
    # FOR CITY IN STATE LIST
    for i in CITY_PART:
        # EXTRACT CITY NAME AND CITY URL
        CITY_URL_PART = i.find_all(CITY_URL_TAG)
        for i in CITY_URL_PART:
            CITY_URL = ALL_BASEURL + i["href"][3:]
            CITY_NAME = i.text.replace(" ", "_").lower()
            CITY_URL_SPLIT = CITY_URL.split("/")

            # MAKE THE SOUP FOR EACH CITY ON THE SCHOOL LIST
            CITY_CONTENT = make_url_request_using_cache(CITY_URL, CACHE_DICT)
            CITY_CONTENT_SOUP = BeautifulSoup(CITY_CONTENT, "html.parser")
            print(CITY_CONTENT_SOUP.find("div", class_="card-body container"))
'''       
