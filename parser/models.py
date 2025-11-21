from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class WeatherTimeSlot:
    time_of_day: str
    temperature: int
    pressure: int
    humidity: int
    weather_phenomenon: str
    perceived_temperature: Optional[int] = None
    wind_speed: Optional[str] = None

@dataclass
class DailyWeather:
    date: datetime
    magnetic_field: int
    magnetic_field_status: str
    time_slots: List[WeatherTimeSlot]
    average_daylight_temperature: Optional[float] = None
    pressure_change_warning: Optional[str] = None

@dataclass
class WeatherForecast:
    city: str
    request_date: datetime
    days: List[DailyWeather]
