"""Tkinter user interface for the weather application."""

import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import requests

from weather_api import get_weather, weather_description

APP_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = APP_DIR / "settings.json"


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather Desktop App")
        self.geometry("560x570")
        self.minsize(500, 520)
        self.configure(bg="#edf3f8")

        self.unit = "C"
        self.last_city = self.load_last_city()
        self.result = None

        self.create_widgets()
        if self.last_city:
            self.city_entry.insert(0, self.last_city)
            self.search_weather()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("TLabel", background="#edf3f8", foreground="#183247")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Temp.TLabel", font=("Segoe UI", 42, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Info.TLabel", font=("Segoe UI", 11))

        container = ttk.Frame(self, padding=22)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="WEATHER DESKTOP APP",
                  style="Title.TLabel").pack(anchor="w", pady=(0, 16))

        search_row = ttk.Frame(container)
        search_row.pack(fill="x", pady=(0, 14))

        self.city_entry = ttk.Entry(search_row, font=("Segoe UI", 12))
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.city_entry.bind("<Return>", lambda _event: self.search_weather())

        self.search_button = ttk.Button(
            search_row, text="Search", command=self.search_weather
        )
        self.search_button.pack(side="left", padx=(8, 0))

        unit_row = ttk.Frame(container)
        unit_row.pack(fill="x")
        ttk.Label(unit_row, text="Temperature unit:").pack(side="left")
        self.unit_button = ttk.Button(
            unit_row, text="°C  /  °F", command=self.toggle_unit
        )
        self.unit_button.pack(side="right")

        self.status_label = ttk.Label(
            container, text="Enter a city to check the weather.",
            style="Info.TLabel"
        )
        self.status_label.pack(anchor="w", pady=(15, 8))

        self.city_label = ttk.Label(container, text="—", style="Section.TLabel")
        self.city_label.pack(anchor="center", pady=(10, 0))

        self.temperature_label = ttk.Label(
            container, text="--°", style="Temp.TLabel"
        )
        self.temperature_label.pack(anchor="center")

        self.description_label = ttk.Label(
            container, text="Current conditions", style="Info.TLabel"
        )
        self.description_label.pack(anchor="center", pady=(0, 18))

        info_frame = ttk.LabelFrame(container, text="Current conditions", padding=14)
        info_frame.pack(fill="x", pady=(0, 18))

        self.feels_label = ttk.Label(info_frame, text="Feels like: —",
                                     style="Info.TLabel")
        self.feels_label.grid(row=0, column=0, sticky="w", padx=8, pady=5)
        self.humidity_label = ttk.Label(info_frame, text="Humidity: —",
                                        style="Info.TLabel")
        self.humidity_label.grid(row=0, column=1, sticky="w", padx=8, pady=5)
        self.wind_label = ttk.Label(info_frame, text="Wind: —",
                                    style="Info.TLabel")
        self.wind_label.grid(row=1, column=0, sticky="w", padx=8, pady=5)

        ttk.Label(container, text="3-DAY FORECAST",
                  style="Section.TLabel").pack(anchor="w", pady=(0, 8))

        self.forecast_frame = ttk.Frame(container)
        self.forecast_frame.pack(fill="x")
        self.forecast_labels = []
        for _ in range(3):
            card = ttk.LabelFrame(self.forecast_frame, padding=10)
            card.pack(side="left", fill="both", expand=True, padx=(0, 7))
            label = ttk.Label(card, text="—", justify="center",
                              style="Info.TLabel")
            label.pack(expand=True)
            self.forecast_labels.append(label)

        ttk.Label(
            container,
            text="Weather data provided by Open-Meteo",
            foreground="#647b8d"
        ).pack(anchor="center", pady=(18, 0))

    def load_last_city(self):
        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as file:
                return json.load(file).get("last_city", "")
        except (OSError, json.JSONDecodeError):
            return ""

    def save_last_city(self, city):
        try:
            with SETTINGS_FILE.open("w", encoding="utf-8") as file:
                json.dump({"last_city": city}, file, indent=2)
        except OSError:
            self.status_label.config(text="Could not save the last searched city.")

    def search_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showinfo("Missing city", "Please enter a city name.")
            return

        self.search_button.config(state="disabled")
        self.status_label.config(text=f"Loading weather for {city}...")
        thread = threading.Thread(
            target=self.fetch_weather, args=(city,), daemon=True
        )
        thread.start()

    def fetch_weather(self, city):
        try:
            data = get_weather(city)
            self.after(0, self.display_weather, data)
        except ValueError as error:
            self.after(0, self.show_error, str(error))
        except requests.RequestException:
            self.after(
                0, self.show_error,
                "Could not connect to the weather service. Check your internet connection."
            )
        except (KeyError, TypeError, IndexError):
            self.after(0, self.show_error, "The weather service returned unexpected data.")

    def show_error(self, message):
        self.search_button.config(state="normal")
        self.status_label.config(text=message)

    def display_weather(self, data):
        self.search_button.config(state="normal")
        self.result = data
        location = data["location"]
        self.city_label.config(
            text=f'{location["name"]}, {location["country"]}'.strip(", ")
        )
        self.description_label.config(
            text=weather_description(data["current"]["weather_code"])
        )
        self.status_label.config(text="Weather updated successfully.")
        self.save_last_city(location["name"])
        self.update_temperature_labels()

    def to_display_unit(self, celsius):
        if self.unit == "F":
            return celsius * 9 / 5 + 32
        return celsius

    def update_temperature_labels(self):
        if not self.result:
            return

        current = self.result["current"]
        symbol = "°" + self.unit
        temperature = self.to_display_unit(current["temperature_2m"])
        feels = self.to_display_unit(current["apparent_temperature"])

        self.temperature_label.config(text=f"{temperature:.1f}{symbol}")
        self.feels_label.config(text=f"Feels like: {feels:.1f}{symbol}")
        self.humidity_label.config(
            text=f'Humidity: {current["relative_humidity_2m"]}%'
        )
        self.wind_label.config(text=f'Wind: {current["wind_speed_10m"]} km/h')

        daily = self.result["daily"]
        for index, label in enumerate(self.forecast_labels):
            date = daily["time"][index]
            minimum = self.to_display_unit(daily["temperature_2m_min"][index])
            maximum = self.to_display_unit(daily["temperature_2m_max"][index])
            description = weather_description(daily["weather_code"][index])
            label.config(
                text=f"{date}\n{description}\n"
                     f"{minimum:.0f}{symbol} / {maximum:.0f}{symbol}"
            )

    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.update_temperature_labels()


if __name__ == "__main__":
    WeatherApp().mainloop()
