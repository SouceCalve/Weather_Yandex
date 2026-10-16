import re
from typing import Optional, Tuple
from datetime import datetime, timedelta


def normalize_time_of_day(text: str) -> str:
    text_lower = text.lower()
    if "утр" in text_lower:
        return "утром"
    elif "дн" in text_lower:
        return "днем"
    elif "вечер" in text_lower:
        return "вечером"
    elif "ноч" in text_lower:
        return "ночью"
    return text


def extract_temperature(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"([+\-−]?\d+)\s*°", text)
    if match:
        temp_str = match.group(1)
        temp_str = temp_str.replace("−", "-")
        return int(temp_str)
    return None


def extract_pressure(text: str) -> int:
    match = re.search(r"(\d{3,4})\s*(?:мм|mmHg|мм\s*рт\.?\s*ст\.?)", text)
    if match:
        return int(match.group(1))
    match = re.search(r"давление[^\d]*(\d{3,4})", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"\b(\d{3,4})\b", text)
    if match:
        return int(match.group(1))
    return 750


def extract_humidity(text: str) -> int:
    match = re.search(r"(\d{1,3})\s*%", text)
    if match:
        return int(match.group(1))
    match = re.search(r"влажность[^\d]*(\d{1,3})", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 60


def get_magnetic_status(value: int) -> str:
    if value <= 2:
        return "спокойное"
    elif value <= 4:
        return "неспокойное"
    elif value <= 6:
        return "слабая магнитная буря"
    elif value <= 8:
        return "магнитная буря"
    else:
        return "сильная магнитная буря"


def parse_date(date_text: str, day_index: int) -> datetime:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    months = {
        "январ": 1,
        "феврал": 2,
        "март": 3,
        "апрел": 4,
        "май": 5,
        "июн": 6,
        "июл": 7,
        "август": 8,
        "сентябр": 9,
        "октябр": 10,
        "ноябр": 11,
        "декабр": 12,
    }
    full_date_match = re.search(r"(\d{1,2})\s+(\w+)", date_text.lower())
    if full_date_match:
        day_num = int(full_date_match.group(1))
        month_text = full_date_match.group(2)
        for month_name, month_num in months.items():
            if month_name in month_text:
                year = today.year
                if month_num < today.month or (
                    month_num == today.month and day_num < today.day
                ):
                    year = today.year + 1
                return datetime(year, month_num, day_num)
    if "сегодня" in date_text.lower():
        return today
    elif "завтра" in date_text.lower():
        return today + timedelta(days=1)
    elif "послезавтра" in date_text.lower():
        return today + timedelta(days=2)
    else:
        return today + timedelta(days=day_index)


def parse_hourly_hidden(text: str) -> Tuple[Optional[str], Optional[int]]:
    phenomenon = None
    feels = None
    if not text:
        return phenomenon, feels
    phenomenon_match = re.search(
        r"^\d{1,2}:\d{2}:\s*[+\-−]?\d+°,\s*(.+?),\s*Ощущается", text
    )
    if phenomenon_match:
        phenomenon = phenomenon_match.group(1).strip()
    feels_match = re.search(r"Ощущается как\s*([+\-−]?\d+)", text)
    if feels_match:
        feels = int(feels_match.group(1).replace("−", "-"))
    return phenomenon, feels


def parse_precipitation(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d+)\s*%", text)
    if match:
        return int(match.group(1))
    return None
