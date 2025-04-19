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
    specs = get_element_text((By.CSS_SELECTOR, 'div[data-testid="ad-parameters-container"]'))
    description = get_element_text((By.CSS_SELECTOR, 'div[data-testid="ad_description"]'))
    price = get_element_text((By.CSS_SELECTOR, 'div[data-testid="ad-price-container"]'))
    location = get_element_text((By.CSS_SELECTOR, 'div[class="css-13l8eec"]'))
    # date = get_element_text((By.CSS_SELECTOR, 'span[data-cy="ad-posted-at"]')) #czasami jest data, czasami jest "dzisiaj o ..."
    title = get_element_text((By.CSS_SELECTOR, 'div[data-testid="ad_title"]'))
    ad_id = get_element_text((By.CSS_SELECTOR, 'span[class="css-w85dhy"]'))
    breadcrumbs = get_elements_text((By.CSS_SELECTOR, 'ol[data-testid="breadcrumbs"] li'))
    if len(breadcrumbs) >= 4:
        brand = breadcrumbs[3]
    else:
        brand = "Pozostałe osobowe"
    add_to_csv(specs, price, location, title, ad_id, brand, url, description)
    return


def add_to_csv(specs, price, location, title, ad_id, brand, url, description):
    csv_target = "cars.csv"
    dictionary = {column: "" for column in [
        "Numer VIN", "Model", "Rok produkcji", "Paliwo", "Typ nadwozia", "Przebieg",
        "Kolor", "Poj. silnika", "Stan techniczny", "Skrzynia biegów", "Kraj pochodzenia",
        "Moc silnika", "Napęd", "Kierownica", "Cena", "Lokalizacja", "Województwo",
        "Tytuł", "Rodzaj ogłoszenia", "Znalezione o", "Link", "ID", "Producent"
    ]}
    id = ad_id.replace("ID:", "").strip()
    print(datetime.now(), "Processing ID", id)
    existing_ids = set()

    try:
        with open(csv_target, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_ids.add(row["ID"])
    except FileNotFoundError:
        pass

    if id in existing_ids:
        print("ID" , id, "already exists, skipping.")
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

    with open(csv_target, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=dictionary.keys())

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(dictionary)
    print("ID", id, "not found, adding to file with data: ", dictionary)
    return


def get_ads():
    driver.get("https://www.olx.pl/motoryzacja/samochody/")
    ads = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="l-card"]')
    links = []
    for ad in ads:
        try:
            link = ad.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            if (link.find("otomoto") == -1):
                links.append(link)
        except Exception as e:
            print(f"Error: {e}")
    print("Got ", len(links), " URLs to scrape from.")
    return links

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

try:
    while True:
        for link in get_ads():
            scrape_url(link)
        print(datetime.now(), "Scrape complete; waiting for 10 minutes before trying again...")
        time.sleep(10 * 60)
except KeyboardInterrupt:
    print("Scraper stopped by user")
    driver.quit()
    exit(1)


