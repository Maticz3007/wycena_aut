import logging

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


def get_element_text(locator, retries=5):
    for i in range(retries):
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            return element.text.strip()
        except StaleElementReferenceException:
            continue
    return Exception('Element not found')


def get_elements_text(locator, retries=5):
    for i in range(retries):
        try:
            elements = wait.until(EC.presence_of_all_elements_located(locator))
            return [element.text.strip() for element in elements]
        except StaleElementReferenceException:
            continue
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
        # date = get_element_text((By.CSS_SELECTOR, 'span[data-cy="ad-posted-at"]')) #czasami jest data, czasami jest "dzisiaj o ...", nie są to dane potrzebme
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
    id = ad_id.replace("ID:", "").strip()
    logging.info("Processing ID %s", id)


    if id in existing_ids:
        logging.info("ID %s already exists, skipping.", id)
        return
    specs_copy = specs.splitlines().copy()
    for item in specs_copy[1:]:
        key, value = item.split(": ")
        dictionary[key.strip()] = value.strip()

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
    logging.info("ID %s not found, adding to file.", id)
    with open(CSV_TARGET, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=dictionary.keys())

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(dictionary)
    existing_ids.add(id)
    return


def get_ads():
    current_url = "https://www.olx.pl/motoryzacja/samochody/"
    links = []
    for i in range(1, 26):
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
        logging.info("Scraper found %s URLs to scrape from.", len(ads))
        try:
            current_url = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-forward"]').get_attribute('href')
        except Exception as e:
            if i==25:
                logging.info("Scraper obtained all available pages.")
            else:
                logging.error("Scraper failed to find next page, current page = %s", i)
    logging.info("Scraper found a total of %s URLs to scrape from.", len(links))

    return links

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# "main"


driver = init_driver()
wait = WebDriverWait(driver, 30)
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', encoding="utf-8",
                    handlers=[logging.StreamHandler(), logging.FileHandler("scrape.log")],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

existing_ids = set()
try:
    with open(CSV_TARGET, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_ids.add(row["ID"])
except FileNotFoundError:
    pass



try:
    logging.warning("Scraper active.")
    while True:
        for link in get_ads():
            scrape_url(link)
        logging.warning("Scrape complete; waiting for 6 hours before trying again...")
        logging.info("Consider running the scraper manually sometime later.")
        time.sleep(6 * 60 * 60)
except KeyboardInterrupt:
    logging.critical("Scraper stopped by user")
    driver.quit()
    exit(1)


