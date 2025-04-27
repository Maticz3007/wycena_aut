import numpy as np
import pandas as pd

CHECKED_COLUMNS = [
        "Model", "Rok produkcji", "Paliwo", "Typ nadwozia", "Przebieg",
        "Kolor", "Poj. silnika", "Stan techniczny", "Skrzynia biegów",
        "Moc silnika", "Cena", "Lokalizacja", "Województwo", "Tytuł",
        "Rodzaj ogłoszenia", "Znalezione o", "Link", "ID", "Producent"
    ]

def clear_invalid_VIN_numbers(vin):
    if len(vin)==17:
        return vin
    else:
        return np.nan

def is_price_negotiable(price):
    if price.find("\ndonegocjacji") == -1:
        return False
    else:
        return True

def clean_price(price):
    return price.strip("\ndonegocjacji").replace(',', ".")

def is_a_rental(df):
    return df['Cena'] <= 5000 and df['Rok produkcji'] >= 2015


CSV_TARGET = "cars.csv"
cars_accepted = pd.read_csv(CSV_TARGET)

for column in CHECKED_COLUMNS:
    cars_accepted = cars_accepted[cars_accepted[column].notnull()]

cars_accepted["Numer VIN"] = cars_accepted["Numer VIN"].astype(str).apply(clear_invalid_VIN_numbers)
cars_accepted["Czy cena do negocjacji"] = cars_accepted["Cena"].astype(str).apply(is_price_negotiable)
cars_accepted["Cena"] = cars_accepted["Cena"].astype(str).apply(clean_price).astype(float)
rental_mask = cars_accepted.apply(is_a_rental, axis=1)
cars_accepted = cars_accepted[~rental_mask]


cars_accepted = cars_accepted[cars_accepted["Rok produkcji"] >= 1990]
cars_accepted = cars_accepted[cars_accepted["Przebieg"] >= 5000]
cars_accepted = cars_accepted[cars_accepted["Poj. silnika"] >= 500]
cars_accepted = cars_accepted[cars_accepted["Poj. silnika"] <= 7000]
cars_accepted = cars_accepted[cars_accepted["Moc silnika"] >= 20]
cars_accepted = cars_accepted[cars_accepted["Moc silnika"] <= 800]
cars_accepted = cars_accepted[cars_accepted["Cena"] >= 1000]


cars_accepted.to_csv("cars_cleaned.csv", index=False)
cars_accepted.info()
cars_rejected = pd.read_csv(CSV_TARGET)
cars_rejected["Numer VIN"] = cars_rejected["Numer VIN"].astype(str).apply(clear_invalid_VIN_numbers)
cars_rejected["Czy cena do negocjacji"] = cars_rejected["Cena"].astype(str).apply(is_price_negotiable)
cars_rejected["Cena"] = cars_rejected["Cena"].astype(str).apply(clean_price).astype(float)
rental_mask = cars_rejected.apply(is_a_rental, axis=1)
cars_rejected = cars_rejected[~rental_mask]
cars_rejected.info()

cars_rejected = pd.concat([cars_rejected, cars_accepted]).drop_duplicates(keep=False)

# Save the discarded data to a new CSV file
cars_rejected.to_csv("cars_discarded.csv", index=False)
