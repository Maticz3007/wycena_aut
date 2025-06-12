import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import joblib
import pandas as pd

cars = pd.read_csv('../datasets/cars_cleaned.csv')
loaded_model = joblib.load("../pricing/model_pipeline.joblib")


def get_column_values(name):
    return sorted(cars[name].dropna().unique().tolist())


def predict_price():
    try:
        dane = {
        "Model": model_var.get(),
        "Paliwo": paliwo_var.get(),
        "Typ nadwozia": nadwozie_var.get(),
        "Przebieg": przebieg_var.get(),
        "Kolor": kolor_var.get(),
        "Poj. silnika": poj_silnik_var.get(),
        "Skrzynia biegów": skrzynia_var.get(),
        "Kraj pochodzenia": kraj_var.get(),
        "Moc silnika": moc_var.get(),
        "Napęd": naped_var.get(),
        "Kierownica": kierownica_var.get(),
        "Województwo": wojewodztwo_var.get(),
        "Rodzaj ogłoszenia": ogloszenie_var.get(),
        "Producent": producent_var.get(),
        "Czy cena do negocjacji": negocjacja_var.get(),
        "Roczny przebieg": int(przebieg_var.get()) / (2025.35 - int(rok_var.get())),
        "Wiek": 2025 - int(rok_var.get()),
        }
        auto = pd.DataFrame([dane])
        wynik = f"Wycena: {loaded_model.predict(auto)[0].astype(int)} zł"
        wynik_label.config(text=wynik)

    except ValueError:
        wynik_label.config(text=f"Błąd: Nieprawidłowe dane liczbowe.")

FONT=("Arial", 14)


def create_combobox(display_name, internal_name, var, row, col):
    ttk.Label(root, text=display_name, font=FONT).grid(row=row, column=col, sticky="w", padx=10, pady=2)
    combo = ttk.Combobox(root, textvariable=var, values=get_column_values(internal_name), font=FONT)
    combo.grid(row=row + 1, column=col, padx=10, pady=2)
    combo.bind('<Map>', lambda e: combo.tk.eval(
        f'[ttk::combobox::PopdownWindow {combo}].f.l configure -font {{Arial {FONT[1]}}}'))

def create_numerical_input(display_name, var, row, col):
    ttk.Label(root, text=display_name, font=FONT).grid(row=row, column=col, sticky="w", padx=10, pady=2)
    entry = ttk.Entry(root, textvariable=var, font=FONT)
    entry.grid(row=row+1, column=col, padx=10, pady=2)

root = tb.Window(themename="superhero")
root.title("Program do wyceny aut")
root.geometry("960x400")
root.columnconfigure((0, 1, 2, 3), weight=1)

model_var = tk.StringVar()
paliwo_var = tk.StringVar()
nadwozie_var = tk.StringVar()
przebieg_var = tk.StringVar()
kolor_var = tk.StringVar()
poj_silnik_var = tk.StringVar()
skrzynia_var = tk.StringVar()
kraj_var = tk.StringVar()
moc_var = tk.StringVar()
naped_var = tk.StringVar()
kierownica_var = tk.StringVar()
wojewodztwo_var = tk.StringVar()
ogloszenie_var = tk.StringVar()
producent_var = tk.StringVar()
negocjacja_var = tk.BooleanVar()
rok_var = tk.IntVar()

create_combobox("Producent", "Producent", producent_var, 0, 0)
create_combobox("Model", "Model", model_var, 0, 1)
create_combobox("Napęd", "Napęd", naped_var, 0, 2)
create_combobox("Nadwozie", "Typ nadwozia", nadwozie_var, 0, 3)

create_combobox("Kierownica", "Kierownica", kierownica_var, 2, 0)
create_combobox("Województwo", "Województwo", wojewodztwo_var, 2, 1)
create_combobox("Rodzaj ogłoszenia", "Rodzaj ogłoszenia", ogloszenie_var, 2, 2)
create_combobox("Kolor", "Kolor", kolor_var, 2, 3)

create_combobox("Paliwo", "Paliwo", paliwo_var, 4, 0)
create_combobox("Skrzynia biegów", "Skrzynia biegów", skrzynia_var, 4, 1)
create_combobox("Kraj pochodzenia", "Kraj pochodzenia", kraj_var, 4, 2)
create_numerical_input("Przebieg (km)", przebieg_var, 4, 3)

create_numerical_input("Pojemność silnika (cm^3)", poj_silnik_var, 6, 0)
create_numerical_input("Moc silnika", moc_var, 6, 1)

ttk.Label(root, text="Rok produkcji:", font=FONT).grid(row=6, column=2, sticky="w", padx=10, pady=2)
rok_spinbox = tk.Spinbox(root, from_=1990, to=2025, textvariable=rok_var, font=FONT, width=10)
rok_spinbox.grid(row=7, column=2, padx=10, pady=2)

check = tk.Checkbutton(root, text="Cena do negocjacji", variable=negocjacja_var, font=FONT)
check.grid(row=7, column=3, padx=10, pady=10)

ttk.Button(root, text="Wyceń", command=predict_price).grid(row=8, column=0, columnspan=4, pady=10)
wynik_label = ttk.Label(root, text="Tutaj pojawi się wycena.", font=FONT)
wynik_label.grid(row=9, column=0, columnspan=4, pady=10)


root.mainloop()

