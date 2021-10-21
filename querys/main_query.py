import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver

def querys(query, owned_domain, excluded_urls_list):
    '''
    query = string: the search query that we will use to find potential websites
    owned_domain = string: define your website - we'll use the latter to exclude the sites that have already linked to you
    exclude_urls = list: domain names to exclude (I've listed some general ones that won't interest you or have "nofollow" attributes)
            example:['forums', 'forum', 'comment', 'comments', 'wikipedia',
                   'youtube', 'facebook', 'instagram', 'pinterest', 'ebay',
                   'tripadvisor', 'reddit', 'twitter', 'flickr', 'amazon', 'etsy',
                   'dailymotion', 'linkedin', 'google', 'aliexpress']



    '''
    try:
        search_query_string(query, excluded_urls_list)
    except Exception as e:
        print(e)


def search_query_string(query, exclude_urls):
    for exclude in exclude_urls:
        query = query + " -inurl:" + exclude

    import urllib
    query = urllib.parse.quote_plus(query)

    number_result = 20  # You may define more, but it will take longer
    try:
        get_online(query, number_result)
    except Exception as e:
        print(e)


def get_online(query, number_result):
    ua = UserAgent()
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')  # Change this to your ChromeDriver path.
    google_url = "https://www.google.com/search?q=" + query + "&num=" + str(number_result)
    response = requests.get(google_url, {"User-Agent": ua.random})
    soup = BeautifulSoup(response.text, "html.parser")

    result_div = soup.find_all('div', attrs={'class': 'g'})

    links = []
    titles = []
    descriptions = []
    for r in result_div:
        try:
            link = r.find('a', href=True)
            title = r.find('h3', attrs={'class': 'r'}).get_text()
            description = r.find('span', attrs={'class': 'st'}).get_text()

            if link != '' and title != '' and description != '':
                links.append(link['href'])
            print(link)
        except:
            continue


