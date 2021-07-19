import requests
from bs4 import BeautifulSoup
from duckduckgo_search import ddg
from csv import writer


def get_phish_data(count: int):
    response = requests.get('https://openphish.com/')
    soup = BeautifulSoup(response.text, 'lxml')
    phish_rows = soup.find('tbody').find_all('tr')
    phish_data = []

    for i in range(count):
        url, targeted_brand, _ = phish_rows[i].find_all('td')
        phish_data.append({'url': url.text, 'targeted brand': targeted_brand.text})

    return phish_data


def duckduckgo_search(text, count: int):
    duck_response = ddg(text, region='wt-wt', safesearch='Off', max_results=count)
    return [duck_element['href'] for duck_element in duck_response]


def google_search(text, count: int):
    google_response = requests.get(text)
    google_soup = BeautifulSoup(google_response.text, 'lxml')
    google_urls = [google_element.a['href'] for google_element in google_soup.find_all('div', class_='kCrYT')
                   if google_element.a]
    google_result = []
    for i in range(count):
        google_result.append(google_urls[i][google_urls[i].find('https://'):google_urls[i].find('&')])
    return google_result


def search_phish_repo(phish_element, count: int):
    if count > 10:
        raise Exception('Вы ввели число большее 10!')
    try:
        duck_urls_no_quot = duckduckgo_search(text='site:https://github.com phish ' + phish_element['targeted brand'],
                                              count=count)
        duck_urls_quot = duckduckgo_search(text=f'site:https://github.com phish "{phish_element["targeted brand"]}"',
                                           count=count)
    except IndexError:
        duck_urls_no_quot = []
        duck_urls_quot = []
    google_urls_no_quot = google_search(text='https://www.google.com/search?q=site:https://github.com phish ' +
                                             phish_element['targeted brand'], count=count)
    google_urls_quot = google_search(text='https://www.google.com/search?q=site:https://github.com phish '
                                          f'"{phish_element["targeted brand"]}"', count=count)

    return ((google_urls_no_quot, 'no quotation', 'google'),
            (google_urls_quot, 'quotation', 'google'),
            (duck_urls_no_quot, 'no quotation', 'duckduckgo'),
            (duck_urls_quot, 'quotation', 'duckduckgo'))


def save2csv(data):
    with open('result.csv', 'w') as file:
        wr = writer(file)
        wr.writerow(['url_phish', 'targeted brand', 'type', 'searcher', 'git url'])
        for row in data:
            wr.writerow(row.values())


if __name__ == '__main__':
    number_of_phishing_sites = 2
    number_of_links_from_search_engines = 2
    full_data = []

    for phish in get_phish_data(number_of_phishing_sites):
        for search_results in search_phish_repo(phish, number_of_links_from_search_engines):
            for search_url in search_results[0]:
                full_data.append({
                    'url_phish': phish['url'],
                    'targeted brand': phish['targeted brand'],
                    'type': search_results[1],
                    'searcher': search_results[2],
                    'git url': search_url
                })

    save2csv(full_data)
