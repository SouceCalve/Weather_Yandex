from dataclasses import dataclass, field
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

    def to_dict(self) -> dict:
        return {
            "time_of_day": self.time_of_day,
            "temperature": self.temperature,
            "perceived_temperature": self.perceived_temperature,
            "pressure": self.pressure,
            "humidity": self.humidity,
            "weather_phenomenon": self.weather_phenomenon,
            "wind_speed": self.wind_speed,
        }


@dataclass
class DailyWeather:
    date: datetime
    magnetic_field: int
    magnetic_field_status: str
    time_slots: List[WeatherTimeSlot]
    average_daylight_temperature: Optional[float] = None
    pressure_change_warning: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat() if self.date else None,
            "magnetic_field": self.magnetic_field,
            "magnetic_field_status": self.magnetic_field_status,
            "time_slots": [slot.to_dict() for slot in self.time_slots],
            "average_daylight_temperature": self.average_daylight_temperature,
            "pressure_change_warning": self.pressure_change_warning,
        }


@dataclass
class HourlyWeatherSlot:
    time: str
    datetime: Optional[datetime] = None
    temperature: Optional[int] = None
    perceived_temperature: Optional[int] = None
    weather_phenomenon: Optional[str] = None
    precipitation_probability: Optional[int] = None
    pressure: Optional[int] = None
    humidity: Optional[int] = None
    wind_speed: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "temperature": self.temperature,
            "perceived_temperature": self.perceived_temperature,
            "weather_phenomenon": self.weather_phenomenon,
            "precipitation_probability": self.precipitation_probability,
            "pressure": self.pressure,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
        }


@dataclass
class WeatherForecast:
    city: str
    request_date: datetime
    days: List[DailyWeather]
    hourly: List[HourlyWeatherSlot] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "city": self.city,
            "request_date": self.request_date.isoformat(),
            "days": [day.to_dict() for day in self.days],
            "hourly": [slot.to_dict() for slot in self.hourly],
        }
