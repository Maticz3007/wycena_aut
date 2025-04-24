import logging
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import csv
import time

CSV_TARGET = "cars.csv"
CSS_SELECTORS = {
    "ad_parameters": 'div[data-testid="ad-parameters-container"]',
    "description": 'div[data-testid="ad_description"]',
    "price": 'div[data-testid="ad-price-container"]',
    "location": 'div[class="css-13l8eec"]',
    "title": 'div[data-testid="ad_title"]',
    "ad_id": 'span[class="css-w85dhy"]',
    "breadcrumbs": 'ol[data-testid="breadcrumbs"] li',
}


def get_element_text(locator):
    try:
        element = wait.until(EC.presence_of_element_located(locator))
        return element.text.strip()
    except StaleElementReferenceException:
         logging.error("%s failed to load", locator)
         return Exception('Element not found')



def get_elements_text(locator):
    try:
        elements = wait.until(EC.presence_of_all_elements_located(locator))
        return [element.text.strip() for element in elements]
    except StaleElementReferenceException:
        logging.error("%s failed to load", locator)
        return Exception('Element not found')



def scrape_url(url):
    driver.get(url)
    try:
        specs = get_element_text((By.CSS_SELECTOR, CSS_SELECTORS["ad_parameters"]))
        description = get_element_text((By.CSS_SELECTOR, CSS_SELECTORS["description"]))
        price = get_element_text((By.CSS_SELECTOR, CSS_SELECTORS["price"]))
        location = get_element_text((By.CSS_SELECTOR, CSS_SELECTORS["location"]))
        title = get_element_text((By.CSS_SELECTOR, CSS_SELECTORS["title"]))
        ad_id = get_element_text((By.CSS_SELECTOR, CSS_SELECTORS["ad_id"]))
        breadcrumbs = get_elements_text((By.CSS_SELECTOR, CSS_SELECTORS["breadcrumbs"]))
        if len(breadcrumbs) >= 4:
            brand = breadcrumbs[3]
        else:
            brand = "Pozostałe osobowe"
        add_to_csv(specs, price, location, title, ad_id, brand, url, description)
    except Exception as e:
        logging.error("Failed to load advertisement %s, skipping", url)
        logging.error(e)
    return


def add_to_csv(specs, price, location, title, ad_id, brand, url, description):
    dictionary = {column: "" for column in [
        "Numer VIN", "Model", "Rok produkcji", "Paliwo", "Typ nadwozia", "Przebieg",
        "Kolor", "Poj. silnika", "Stan techniczny", "Skrzynia biegów", "Kraj pochodzenia",
        "Moc silnika", "Napęd", "Kierownica", "Cena", "Lokalizacja", "Województwo",
        "Tytuł", "Rodzaj ogłoszenia", "Znalezione o", "Link", "ID", "Producent"
    ]}

    specs_copy = specs.splitlines().copy()
    for item in specs_copy[1:]:
        key, value = item.split(": ")
        dictionary[key.strip()] = value.strip()
    id = ad_id.replace("ID:", "").strip()
    dictionary["ID"] = id
    dictionary["Producent"] = brand
    dictionary["Cena"] = price.replace("zł", "").replace(" ", "").strip()
    place = location.replace("LOKALIZACJA", "").strip().split('\n')
    dictionary["Lokalizacja"] = place[0].replace(",", "").strip()
    dictionary["Województwo"] = place[1].strip()
    dictionary["Tytuł"] = title
    dictionary["Przebieg"] = dictionary["Przebieg"].replace("km", "").replace(" ", "")
    dictionary["Poj. silnika"] = dictionary["Poj. silnika"].replace("cm³", "").replace(" ", "")
    dictionary["Moc silnika"] = dictionary["Moc silnika"].replace("KM", "").replace(" ", "")
    dictionary["Rodzaj ogłoszenia"] = specs_copy[0]
    dictionary["Znalezione o"] = datetime.now()
    dictionary["Link"] = url
    dictionary["Opis"] = description.replace("OPIS\n", "").strip()

    with open(CSV_TARGET, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=dictionary.keys())
        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(dictionary)
    logging.info("%s: ID %s added to file.", url, id)
    existing_links.add(url)
    return


def get_ads():
    current_url = "https://www.olx.pl/motoryzacja/samochody/"
    links = []
    i=0
    while True:
        try:
            i=i+1
            driver.get(current_url)
            logging.info("Scraper obtained page %s.", i)
            ads = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="l-card"]')

            for ad in ads:
                try:
                    link = ad.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    if (link.find("otomoto") == -1):
                        links.append(link)
                except Exception as e:
                    logging.critical(f"Error: {e}")

            current_url = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-forward"]').get_attribute('href')

        except NoSuchElementException:
            logging.warning("Scraper reached the last page of listings.")
            break
    if(len(links)==0):
        pass
    logging.info("Scraper found a total of %s URLs to scrape from.", len(links))
    return links

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_existing_links():
    existing_links = set()
    try:
        with open(CSV_TARGET, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_links.add(row["Link"])
    except FileNotFoundError:
        pass
    return existing_links

# "main"


driver = init_driver()
wait = WebDriverWait(driver, 20)
existing_links=get_existing_links()
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', encoding="utf-8",
                    handlers=[logging.StreamHandler(), logging.FileHandler("scrape.log")],
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    logging.info("Scraper active.")
    while True:
        for link in get_ads():
            if link not in existing_links:
                scrape_url(link)
            else:
                logging.info("%s has already been processed, skipping.", link)
        #logging.info("Scrape complete; waiting for 60 minutes before trying again...")
        #time.sleep(60 * 60)
except KeyboardInterrupt:
    logging.critical("Scraper stopped by user")
    driver.quit()



