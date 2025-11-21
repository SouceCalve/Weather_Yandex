from typing import List
import logging
from parser.models import DailyWeather
from config import PRESSURE_CHANGE_THRESHOLD

logger = logging.getLogger(__name__)


def calculate_average_daylight_temperature(day: DailyWeather) -> float:
    daylight_slots = [
        slot
        for slot in day.time_slots
        if slot.time_of_day in ["утром", "днем", "вечером"]
    ]
    if not daylight_slots:
        logger.warning(f"Не найдено дневных временных слотов для {day.date}")
        return 0.0
    total_temp = sum(slot.temperature for slot in daylight_slots)
    return round(total_temp / len(daylight_slots), 1)


def detect_pressure_change(day: DailyWeather) -> str:
    if not day.time_slots:
        return ""

    pressures = [slot.pressure for slot in day.time_slots]
    min_pressure = min(pressures)
    max_pressure = max(pressures)
    pressure_diff = max_pressure - min_pressure

    if pressure_diff < PRESSURE_CHANGE_THRESHOLD:
        return ""

    first_pressure = pressures[0]
    last_pressure = pressures[-1]

    if last_pressure > first_pressure:
        return "ожидается резкое увеличение атмосферного давления"
    elif last_pressure < first_pressure:
        return "ожидается резкое падение атмосферного давления"
    else:
        min_index = pressures.index(min_pressure)
        max_index = pressures.index(max_pressure)
        if max_index > min_index:
            return "ожидается резкое увеличение атмосферного давления"
        else:
            return "ожидается резкое падение атмосферного давления"


class WeatherDataProcessor:
    @staticmethod
    def calculate_average_daylight_temperature(day: DailyWeather) -> float:
        return calculate_average_daylight_temperature(day)

    @staticmethod
    def detect_pressure_change(day: DailyWeather) -> str:
        return detect_pressure_change(day)

    @staticmethod
    def process_forecast(days: List[DailyWeather]) -> List[DailyWeather]:
        processed_days = []
        for day in days:
            avg_temp = WeatherDataProcessor.calculate_average_daylight_temperature(day)
            day.average_daylight_temperature = avg_temp
            pressure_warning = WeatherDataProcessor.detect_pressure_change(day)
            day.pressure_change_warning = pressure_warning
            processed_days.append(day)
        return processed_days
