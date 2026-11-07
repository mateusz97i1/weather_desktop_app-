# Weather Desktop App

A desktop weather application built with Python and Tkinter. It retrieves current weather conditions and a three-day forecast using the free [Open-Meteo API](https://open-meteo.com/).

## Features

- Search for a city by name
- Display current temperature, feels-like temperature, humidity and wind speed
- Show a three-day forecast
- Switch between Celsius and Fahrenheit
- Handle unknown cities and connection errors
- Save the last searched city locally in `settings.json`

## Technologies

- Python
- Tkinter
- Requests
- REST API and JSON
- pytest
- Git

## Setup

Python 3.10 or newer is recommended.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/weather-desktop-app.git
cd weather-desktop-app
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

## Run tests

```bash
pytest
```

## Data source

Weather information is provided by Open-Meteo. No API key is required.

## Project structure

```text
weather-desktop-app/
├── main.py
├── gui.py
├── weather_api.py
├── requirements.txt
├── tests/
│   └── test_weather_api.py
└── README.md
```
