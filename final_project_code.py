from bs4 import BeautifulSoup
import requests
import json
import secrets  # file that contains your API key
import time


BASE_URL_1 = "https://www.lib.umich.edu"
BASE_URL_2 = "https://www.lib.umich.edu/locations-and-hours"

CACHE_FILENAME = "final_project_cache.json"
CACHE_DICT = {}

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILENAME, 'w')
    contents_to_write = json.dumps(cache_dict)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_request_with_cache_text(url):
    '''Check the cache for a saved result for this url. 
    If the result is found, print "Using Cache" and return it. 
    Otherwise send a new request, print "Fetching", save it, then return it.

    Parameters
    ----------
    url: string

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache

    '''
    if url in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[url]
    else:
        print("Fetching")
        time.sleep(1)
        CACHE_DICT[url] = requests.get(url).text
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]

CACHE_DICT = open_cache()


class UmichLibrary:
    '''a library in University of Michigan

    Instance Attributes
    -------------------
    name: string
        the name of a library

    location: string
        the location of a library 

    hours: string
        the hours of a library 

    phone: string
        the phone of a library
    '''

    def __init__(self, name, location, hours, phone):
        
        self.name = name
        self.location = location
        self.hours = hours
        self.phone = phone


    def info(self):
        return f"{self.name} locates at {self.location}. Hours of {self.hours}.\
        For more information, please contact {self.phone}"


def build_library_url_dict():
    ''' Make a dictionary that maps library name to library page url from "https://www.lib.umich.edu/locations-and-hours"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    library_name_url_dict = {}
    # Make the soup
    response = make_request_with_cache_text(BASE_URL_2)
    soup = BeautifulSoup(response, "html.parser")
    # For each library listed
    library_list = soup.find_all(
        'li', class_="css-77qsxv")

    for item in library_list:
        library_link = item.find('a')['href']
        library_name = item.find('span').text
        state_name_url_dict[library_name.lower()] = BASE_URL_1 + library_link

    return library_name_url_dict


def get_library_instance(library_url):
    '''Make an instances from a library URL.

    Parameters
    ----------
    library_url: string
        The URL for a library page

    Returns
    -------
    instance
        a UmichLibrary instance
    '''

    response = make_request_with_cache_text(library_url)
    soup = BeautifulSoup(response, "html.parser")
    library_name = soup.find('h1', class_="css-1xx2irx-StyledHeading e1tlxttt0").text
    library_location = soup.find('Address')
    library_hours = "Today: 10am - 5pm, by appointment"
    library_phone_div = soup.find('div', class_="css-10ynnyg")
    library_phone = library_phone_div.find('a', class_="css-ilta09-StyledLink e2b8o640").text

    return UmichLibrary(library_name, library_location, library_hours, library_phone)


def get_nearby_restaurants(library_object):
    '''Obtain API data from MapQuest API. Check the cache for a saved result for this resource_url + params:values
    combo. If the result is found, print "Using Cache" and return it. Otherwise send a new request,print "Fetching", 
    save it, then return it.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    resource_url = 'https://api.yelp.com/v3/businesses/search'
    param_strings = []
    connector = '&'
    params = {'key': secrets.YELP_FUSION_API_KEY, 'term': "restaurants", 'location': library_object.location, 'radius': 100,
              'limit': 10}
    for k in params.keys():
        param_strings.append(f'{k}={params[k]}')
    param_strings.sort()
    unique_key = resource_url + '?' + connector.join(param_strings)

    if unique_key in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[unique_key]
    else:
        print("Fetching")
        time.sleep(1)
        CACHE_DICT[unique_key] = requests.get(unique_key).json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]


CACHE_DICT = open_cache()

Shapiro_library = get_library_instance("https://www.lib.umich.edu/locations-and-hours/shapiro-library")
get_nearby_restaurants(Shapiro_library)