import os
import time
import ujson

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Delete files if present
try:
    os.remove('Authors_URL.txt')
    os.remove('scraper_results.json')
except OSError:
    pass


def write_authors(author_list, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        for i in range(0, len(author_list)):
            f.write(author_list[i] + '\n')


def initCrawlerScraper(seed):
    # Initialize driver for Chrome
    web_opt = webdriver.ChromeOptions()
    web_opt.add_experimental_option('excludeSwitches', ['enable-logging'])
    web_opt.add_argument('--ignore-certificate-errors')
    web_opt.add_argument('--incognito')
    web_opt.add_argument('--headless')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(seed)  # Start with the original link

    Links = []  # Array with pure-portal profiles URL
    publication_data = []  # To store publication information for each pure-portal profile

    next_link = int(driver.find_element("css selector", ".nextLink").is_enabled())
    print("Crawler has begun...")
    while next_link:
        page = driver.page_source
        # XML parser to parse each URL
        beautiful_soup = BeautifulSoup(page, "html.parser")

        # Extracting exact URL by splitting string into list
        for link in beautiful_soup.findAll('a', class_='link person'):
            url = str(link)[str(link).find('https://pureportal.coventry.ac.uk/en/persons/'):].split('"')
            Links.append(url[0])
        # Click on Next button to visit next page
        try:
            if driver.find_element("css selector", ".nextLink"):
                elements = driver.find_element("css selector", ".nextLink")
                driver.execute_script("arguments[0].click();", elements)
            else:
                next_link = False
        except NoSuchElementException:
            break
    print("Crawler has found ", len(Links), " pure-portal profiles")
    write_authors(Links, 'Authors_URL.txt')

    print("Scraping publication data for ", len(Links), " pure-portal profiles...")
    for link in Links:
        # Visit each link to get data
        time.sleep(1)
        driver.get(link)
        try:
            if driver.find_elements("css selector", ".portal_link.btn-primary.btn-large"):
                elements = driver.find_elements("css selector", ".portal_link.btn-primary.btn-large")
                for element in elements:
                    if "research output".lower() in element.text.lower():
                        driver.execute_script("arguments[0].click();", element)
                        driver.get(driver.current_url)
                        # Get name of Author
                        name = driver.find_element("css selector", "div[class='header person-details']>h1")
                        request = requests.get(driver.current_url)
                        # Parse all the data via BeautifulSoup
                        soup = BeautifulSoup(request.content, 'html.parser')

                        # Extracting publication name, publication url, date and CU Authors
                        table = soup.find('ul', attrs={'class': 'list-results'})
                        if table is not None:
                            for row in table.findAll('div', attrs={'class': 'result-container'}):
                                data = {'name': row.h3.a.text, 'pub_url': row.h3.a['href']}
                                date = row.find("span", class_="date")

                                data['cu_author'] = name.text
                                data['date'] = date.text
                                print("Publication Name :", row.h3.a.text)
                                print("Publication URL :", row.h3.a['href'])
                                print("CU Author :", name.text)
                                print("Date :", date.text)
                                print("\n")
                                publication_data.append(data)
            else:
                # Get name of Author
                name = driver.find_element("css selector", "div[class='header person-details']>h1")
                request = requests.get(link)
                # Parse all the data via BeautifulSoup
                soup = BeautifulSoup(request.content, 'html.parser')
                # Extracting publication name, publication url, date and CU Authors
                table = soup.find('div', attrs={'class': 'relation-list relation-list-publications'})
                if table is not None:
                    for row in table.findAll('div', attrs={'class': 'result-container'}):
                        data = {"name": row.h3.a.text, 'pub_url': row.h3.a['href']}
                        date = row.find("span", class_="date")

                        data['cu_author'] = name.text
                        data['date'] = date.text
                        print("Publication Name :", row.h3.a.text)
                        print("Publication URL :", row.h3.a['href'])
                        print("CU Author :", name.text)
                        print("Date :", date.text)
                        print("\n")
                        publication_data.append(data)
        except Exception:
            continue

    print("Crawler has scrapped data for ", len(publication_data), " pure-portal publications")
    driver.quit()
    # Writing all the scraped results in a file with JSON format
    with open('scraper_results.json', 'w') as f:
        ujson.dump(publication_data, f)


initCrawlerScraper(
    'https://pureportal.coventry.ac.uk/en/organisations/school-of-computing-mathematics-and-data-sciences/persons/')
