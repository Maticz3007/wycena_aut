import joblib


from transformer import ColumnDropper, RareCategoryGrouper

loaded_model = joblib.load("model_pipeline.joblib")

import pandas as pd

auto = pd.DataFrame([{
    "Model": "ML Klasa",
    "Paliwo": "Benzyna",
    "Typ nadwozia": "Kombi",
    "Przebieg": 273000,
    "Kolor": "Srebrny",
    "Poj. silnika": 3200.0,
    "Skrzynia biegów": "Automatyczna",
    "Kraj pochodzenia": None,
    "Moc silnika": 215.0,
    "Napęd": "4x4 (stały)",
    "Kierownica": "po lewej",
    "Województwo": "Małopolskie",
    "Rodzaj ogłoszenia": "Prywatne",
    "Producent": "Mercedes-Benz",
    "Czy cena do negocjacji": True,
    "Roczny przebieg": 10360.0,
    "Wiek": 26,
    "Poprawność VIN": "Poprawny",
    "Numer VIN": "x",
    "Tytuł": "x",
    "Opis": "x",
    "Link": "x",
    "Lokalizacja": "x",
    "Stan techniczny": "x"
}])

pred = loaded_model.predict(auto)
print(f"Przewidywana wartość auta: {pred[0]} PLN")