"""Functions for retrieving weather data from Open-Meteo."""

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city: str) -> dict:
    """Return the first matching city's name, country and coordinates."""
    params = {
        "name": city.strip(),
        "count": 1,
        "language": "en",
        "format": "json",
    }
    response = requests.get(GEOCODING_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("results"):
        raise ValueError(f"City not found: {city}")

    result = data["results"][0]
    return {
        "name": result["name"],
        "country": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }


def get_weather(city: str) -> dict:
    """Return current conditions and a three-day forecast for a city."""
    location = get_coordinates(city)
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "wind_speed_10m,weather_code"
        ),
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3,
    }

    response = requests.get(WEATHER_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "location": location,
        "current": data["current"],
        "daily": data["daily"],
    }


def weather_description(code: int) -> str:
    """Convert a WMO weather code into a readable description."""
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, "Unknown conditions")
