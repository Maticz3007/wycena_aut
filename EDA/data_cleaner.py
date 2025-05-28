# czyszczenie zbioru z błędnych danych oraz kolumn niepotrzebnych do dalszej analizy

import pandas as pd

CSV_SOURCE = "../datasets/cars.csv"
CSV_OUTPUT = "../datasets/cars_cleaned.csv"
ACCEPTED_FUEL_TYPES = ["Benzyna", "Diesel", "LPG"]
REQUIRED_COLUMNS = [
        "Model", "Rok produkcji", "Paliwo", "Typ nadwozia", "Przebieg",
        "Kolor", "Poj. silnika", "Stan techniczny", "Skrzynia biegów",
        "Moc silnika", "Cena", "Lokalizacja", "Województwo", "Tytuł",
        "Rodzaj ogłoszenia", "Znalezione o", "Link", "ID", "Producent"
    ]


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
        (df["Cena"] <= 400000) &
        (df["Paliwo"].isin(ACCEPTED_FUEL_TYPES)) &
        (df["Przebieg"] <= 600000) &
        (df["Roczny przebieg"] > 5000) &
        (df["Roczny przebieg"] < 36500) &
        (df["Stan techniczny"] == "Nieuszkodzony")
]

df.drop(columns=[ "Hashcode", "Rok produkcji", "ID", "Znalezione o", "Numer VIN",
                  "Tytuł", "Opis", "Link", "Lokalizacja", "Stan techniczny", "Roczny przebieg"], inplace=True)


#wypełnienie "dopuszczalnych" braków

df["Kraj pochodzenia"] = df["Kraj pochodzenia"].fillna("Brak danych")
df["Napęd"] = df["Napęd"].fillna("Brak danych")
df["Kierownica"] = df["Kierownica"].fillna("Brak danych")

print(f"Created a file {CSV_OUTPUT} with {df.shape[0]} rows of data")
df.to_csv(CSV_OUTPUT, index=False)


