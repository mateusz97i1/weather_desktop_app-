from unittest.mock import Mock, patch

import pytest
import requests

from weather_api import get_coordinates, weather_description


@patch("weather_api.requests.get")
def test_get_coordinates_returns_first_result(mock_get):
    response = Mock()
    response.json.return_value = {
        "results": [{
            "name": "Warsaw",
            "country": "Poland",
            "latitude": 52.23,
            "longitude": 21.01,
        }]
    }
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = get_coordinates("Warsaw")

    assert result["name"] == "Warsaw"
    assert result["country"] == "Poland"
    assert result["latitude"] == 52.23


@patch("weather_api.requests.get")
def test_get_coordinates_raises_when_city_not_found(mock_get):
    response = Mock()
    response.json.return_value = {}
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with pytest.raises(ValueError, match="City not found"):
        get_coordinates("NoSuchCity")


def test_weather_description():
    assert weather_description(0) == "Clear sky"
    assert weather_description(999) == "Unknown conditions"
