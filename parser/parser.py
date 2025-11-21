import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional, Tuple
import logging
from parsers.models import WeatherForecast, DailyWeather, WeatherTimeSlot
from config import YANDEX_WEATHER_BASE_URL, REQUEST_TIMEOUT, USER_AGENT
from parsers.utils import (
    normalize_time_of_day, extract_temperature, extract_pressure,
    extract_humidity, get_magnetic_status, parse_date
)

logger = logging.getLogger(__name__)

class YandexWeatherParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def get_city_url(self, city: str) -> str:
        search_url = f"{YANDEX_WEATHER_BASE_URL}"
        city_slug = city.lower().replace(' ', '-')
        return f"{YANDEX_WEATHER_BASE_URL}/{city_slug}"
    
    def parse_weather(self, city: str) -> WeatherForecast:
        url = self.get_city_url(city)
        logger.info(f"Запрос погоды для города: {city}, URL: {url}")
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            days = self._parse_forecast_days(soup)
            forecast = WeatherForecast(
                city=city,
                request_date=datetime.now(),
                days=days
            )
            logger.info(f"Успешно получен прогноз на {len(days)} дней")
            return forecast
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к Яндекс.Погоде: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при парсинге данных: {e}")
            raise
    
    def _parse_forecast_days(self, soup: BeautifulSoup) -> List[DailyWeather]:
        days = []
        day_cards = soup.find_all('li', class_=re.compile(r'AppForecastDay_dayCard'))
        if not day_cards:
            day_cards = soup.find_all('article', class_=re.compile(r'AppForecastDay_container'))
        
        day_cards = day_cards[:7]
        
        for idx, day_card in enumerate(day_cards):
            try:
                daily_weather = self._parse_single_day(day_card, idx)
                if daily_weather:
                    days.append(daily_weather)
            except Exception as e:
                logger.warning(f"Ошибка при парсинге дня {idx}: {e}")
                continue
        
        return days[:7]
    
    def _parse_single_day(self, day_element, day_index: int) -> Optional[DailyWeather]:
        date_text = self._extract_date(day_element, day_index)
        if not date_text:
            return None
        date = parse_date(date_text, day_index)
        magnetic_field, magnetic_status = self._extract_magnetic_field(day_element)
        time_slots = self._extract_time_slots(day_element)
        
        return DailyWeather(
            date=date,
            magnetic_field=magnetic_field,
            magnetic_field_status=magnetic_status,
            time_slots=time_slots
        )
    
    def _extract_date(self, element, day_index: int) -> Optional[str]:
        article = element.find('article', class_=re.compile(r'AppForecastDay_container'))
        search_element = article if article else element
        title = search_element.find('h3', class_=re.compile(r'AppForecastDayHeader_dayTitle'))
        if title:
            text = title.get_text()
            text = text.replace('\xa0', ' ').replace('&nbsp;', ' ').strip()
            return text
        text = search_element.get_text()
        date_patterns = [
            r'(Сегодня|Завтра|Послезавтра)[,\s]+(\d{1,2})\s+(январ|феврал|март|апрел|май|июн|июл|август|сентябр|октябр|ноябр|декабр)',
            r'(\d{1,2})\s+(январ|феврал|март|апрел|май|июн|июл|август|сентябр|октябр|ноябр|декабр)',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        if day_index == 0:
            return "Сегодня"
        elif day_index == 1:
            return "Завтра"
        else:
            return f"через {day_index} дня"
    
    def _extract_magnetic_field(self, element) -> Tuple[int, str]:
        article = element.find('article', class_=re.compile(r'AppForecastDay_container'))
        search_element = article if article else element
        info_block = search_element.find('div', class_=re.compile(r'AppForecastDayDuration_info'))
        if info_block:
            items = info_block.find_all('div', class_=re.compile(r'AppForecastDayDuration_item'))
            for item in items:
                caption = item.find('div', class_=re.compile(r'AppForecastDayDuration_caption'))
                if caption and 'магнитн' in caption.get_text().lower():
                    value_elem = item.find('div', class_=re.compile(r'AppForecastDayDuration_value'))
                    if value_elem:
                        text = value_elem.get_text().strip()
                        match = re.search(r'(\d+)', text)
                        if match:
                            value = int(match.group(1))
                            status_text = text.lower()
                            if 'спокойн' in status_text:
                                status = "спокойное"
                            elif 'неспокойн' in status_text:
                                status = "неспокойное"
                            elif 'буря' in status_text:
                                if 'слаб' in status_text:
                                    status = "слабая магнитная буря"
                                elif 'сильн' in status_text:
                                    status = "сильная магнитная буря"
                                else:
                                    status = "магнитная буря"
                            else:
                                status = get_magnetic_status(value)
                            return value, status
        text = search_element.get_text()
        magnetic_patterns = [
            r'магнитн[а-я]*\s*поле[^\d]*(\d+)',
            r'(\d+)[,\s]+спокойн',
        ]
        for pattern in magnetic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                status = get_magnetic_status(value)
                return value, status
        
        return 3, "спокойное"
    
    def _extract_time_slots(self, element) -> List[WeatherTimeSlot]:
        time_slots = []
        time_prefixes = {
            'm': 'утром',
            'd': 'днем',
            'e': 'вечером',
            'n': 'ночью'
        }
        
        for prefix, time_of_day in time_prefixes.items():
            slot = self._extract_single_time_slot(element, prefix, time_of_day)
            if slot:
                time_slots.append(slot)
        
        return time_slots
    
    def _extract_single_time_slot(self, element, prefix: str, time_of_day: str) -> Optional[WeatherTimeSlot]:
        try:
            article = element.find('article', class_=re.compile(r'AppForecastDay_container'))
            search_element = article if article else element
            if search_element:
                for hidden in search_element.find_all(class_=re.compile(r'visuallyHidden|A11Y_visuallyHidden')):
                    hidden.decompose()
            temp_elem = search_element.find('div', style=re.compile(rf'grid-area:{prefix}-temp'))
            temperature = 0
            if temp_elem:
                temp_text = temp_elem.get_text().strip()
                if temp_text:
                    temp_value = extract_temperature(temp_text)
                    if temp_value is not None:
                        temperature = temp_value
                    else:
                        return None
            else:
                return None
            feels_elem = search_element.find('div', style=re.compile(rf'grid-area:{prefix}-feels'))
            perceived_temperature = None
            if feels_elem:
                feels_text = feels_elem.get_text().strip()
                if feels_text:
                    feels_value = extract_temperature(feels_text)
                    if feels_value is not None:
                        perceived_temperature = feels_value
            text_elem = search_element.find('div', style=re.compile(rf'grid-area:{prefix}-text'))
            weather_phenomenon = "не определено"
            if text_elem:
                weather_phenomenon = text_elem.get_text().strip()
            wind_speed = None
            wind_elems = search_element.find_all('div', style=re.compile(rf'grid-area:{prefix}-wind'))
            for wind_elem in wind_elems:
                wind_formatted = wind_elem.find_next('div', class_=re.compile(r'wind_formatted'))
                if wind_formatted:
                    wind_speed = wind_formatted.get_text().strip()
                    break
                wind_text = wind_elem.get_text().strip()
                if wind_text and re.search(r'\d+', wind_text):
                    match = re.search(r'(\d+)', wind_text)
                    if match:
                        wind_speed = f"{match.group(1)} м/с"
                        break
            hum_elem = search_element.find('div', style=re.compile(rf'grid-area:{prefix}-hum'))
            humidity = 60
            if hum_elem:
                hum_text = hum_elem.get_text().strip()
                if hum_text:
                    humidity = extract_humidity(hum_text)
            press_elem = search_element.find('div', style=re.compile(rf'grid-area:{prefix}-press'))
            pressure = 750
            if press_elem:
                press_text = press_elem.get_text().strip()
                if press_text:
                    pressure = extract_pressure(press_text)
            
            return WeatherTimeSlot(
                time_of_day=time_of_day,
                temperature=temperature,
                pressure=pressure,
                humidity=humidity,
                weather_phenomenon=weather_phenomenon,
                perceived_temperature=perceived_temperature,
                wind_speed=wind_speed
            )
        except Exception as e:
            logger.debug(f"Ошибка при парсинге временного слота {time_of_day}: {e}")
            return None