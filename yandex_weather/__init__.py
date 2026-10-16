import logging
from yandex_weather.parser import YandexWeatherParser
from yandex_weather.processors import WeatherDataProcessor

logger = logging.getLogger(__name__)

_parser = YandexWeatherParser()
_processor = WeatherDataProcessor()


def get_forecast(city: str) -> dict:
    """Возвращает прогноз погоды на 7 дней и почасовой прогноз на
    текущий день для указанного города в виде dict."""
    forecast = _parser.parse_weather(city)
    forecast.days = _processor.process_forecast(forecast.days)
    return forecast.to_dict()


def get_hourly(city: str) -> dict:
    """Возвращает почасовой прогноз на текущий день в виде dict."""
    slots = _parser.parse_hourly_weather(city)
    return {
        "city": city,
        "hourly": [slot.to_dict() for slot in slots],
    }


__all__ = ["get_forecast", "get_hourly"]
