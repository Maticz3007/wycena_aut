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

def clear_invalid_VIN_numbers(vin):
    vin = vin.strip().upper()
    if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
        return np.nan
    return vin

def is_price_negotiable(price):
    if price.find("\ndonegocjacji") == -1:
        return False
    else:
        return True

def clean_price(price):
    return price.strip("\ndonegocjacji").replace(',', ".").strip()

def is_a_rental(df):
    return df['Cena'] <= 5000 and df['Rok produkcji'] >= 2015


df = pd.read_csv(CSV_SOURCE)
df = df.dropna(subset=REQUIRED_COLUMNS)
df.drop(columns=["Znalezione o"], inplace=True)
df["Czy cena do negocjacji"] = df["Cena"].astype(str).apply(is_price_negotiable)
df["Cena"] = df["Cena"].astype(str).apply(clean_price).astype(float)
df["Numer VIN"] = df["Numer VIN"].astype(str).apply(clear_invalid_VIN_numbers)

df_has_vin = df[df["Numer VIN"].notna()]
df_no_vin = df[df["Numer VIN"].isna()]
df_has_vin = df_has_vin[~df_has_vin["Numer VIN"].duplicated(keep="last")]
df = pd.concat([df_has_vin, df_no_vin], ignore_index=True)

rental_mask = df.apply(is_a_rental, axis=1)
df = df[~rental_mask]

df = df[
        (df["Rok produkcji"] >= 1990) &
        (df["Przebieg"] >= 5000) &
        (df["Poj. silnika"] >= 500) & (df["Poj. silnika"] <= 7000) &
        (df["Moc silnika"] >= 20) & (df["Moc silnika"] <= 800) &
        (df["Cena"] >= 1000) & (df["Paliwo"].isin(ACCEPTED_FUEL_TYPES))
]

print(f"Created a file {CSV_OUTPUT} with {df.shape[0]} rows of data")
df.to_csv(CSV_OUTPUT, index=False)



