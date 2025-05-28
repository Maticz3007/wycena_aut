import numpy as np
import pandas as pd
import re

CSV_SOURCE = "cars.csv"
CSV_OUTPUT = "cars_cleaned.csv"
ACCEPTED_FUEL_TYPES = ["Benzyna", "Diesel", "LPG"]
REQUIRED_COLUMNS = [
        "Model", "Rok produkcji", "Paliwo", "Typ nadwozia", "Przebieg",
        "Kolor", "Poj. silnika", "Stan techniczny", "Skrzynia biegów",
        "Moc silnika", "Cena", "Lokalizacja", "Województwo", "Tytuł",
        "Rodzaj ogłoszenia", "Znalezione o", "Link", "ID", "Producent"
    ]

#def clear_invalid_VIN_numbers(vin):
#    vin = vin.strip().upper()
#    if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
#        return np.nan
#    return vin

def is_price_negotiable(price):
    if price.find("\ndonegocjacji") == -1:
        return False
    else:
        return True

def clean_price(price):
    return price.strip("\ndonegocjacji").replace(',', ".").strip()

def is_a_rental(df):
    return 'leasing' in df["Tytuł"].lower() or 'leasing' in df["Opis"].lower()

def generate_hashcode(df) -> int:
    return (df["Rok produkcji"] +
            df["Przebieg"] * 13 +
            df["Poj. silnika"] * 23 +
            df["Moc silnika"] * 31 +
            (df["Cena"]) * 37 +
            generate_hash_from_text(df["Model"]) * 41 +
            generate_hash_from_text(df["Producent"]) * 43)

def generate_hash_from_text(text) -> int:
    return abs(hash(text) % 100_000_000)

def calculate_yearly_mileage(df):
    return df["Przebieg"] / (2025.35 - df["Rok produkcji"])


df = pd.read_csv(CSV_SOURCE)
df = df.dropna(subset=REQUIRED_COLUMNS)

df["Czy cena do negocjacji"] = df["Cena"].astype(str).apply(is_price_negotiable)
df["Cena"] = df["Cena"].astype(str).apply(clean_price).astype(float)
df["Roczny przebieg"] = df.apply(calculate_yearly_mileage, axis=1)
df["Hashcode"] = df.apply(generate_hashcode, axis=1)
df["Wiek"] = 2025 - df["Rok produkcji"]
df = df.drop_duplicates(subset=["Hashcode"])
df.drop(columns=["Hashcode"], inplace=True)

rental_mask = df.apply(is_a_rental, axis=1)
df = df[~rental_mask]

df = df[
        (df["Rok produkcji"] >= 1990) &
        (df["Przebieg"] >= 5000) &
        (df["Poj. silnika"] >= 500) &
        (df["Poj. silnika"] <= 7000) &
        (df["Moc silnika"] >= 20) &
        (df["Moc silnika"] <= 800) &
        (df["Cena"] >= 1000) &
        (df["Paliwo"].isin(ACCEPTED_FUEL_TYPES)) &
        (df["Przebieg"] <= 600000) &
        (df["Roczny przebieg"] > 5000) &
        (df["Roczny przebieg"] < 36500)
]

#df.drop(columns=["Roczny przebieg"], inplace=True)
df.drop(columns=["Rok produkcji"], inplace=True)
df.drop(columns=["ID"], inplace=True)
df.drop(columns=["Znalezione o"], inplace=True)

#df["Numer VIN"] = df["Numer VIN"].astype(str).apply(clear_invalid_VIN_numbers)

print(f"Created a file {CSV_OUTPUT} with {df.shape[0]} rows of data")
df.to_csv(CSV_OUTPUT, index=False)

print(df.sample(10))


