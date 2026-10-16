# yandex_weather

Библиотека для парсинга прогноза погоды с Яндекс.Погоды. Возвращает данные в виде
`dict` — без записи в базу данных, без генерации Excel и без веб-сервера.

Возможности:

- Прогноз на 7 дней (утром / днём / вечером / ночью): температура, ощущаемая
  температура, давление, влажность, явление, ветер, магнитное поле.
- Почасовой прогноз на текущий день (время, температура, ощущаемая температура,
  явление, вероятность осадков).
- Автоматические расчёты: средняя дневная температура и предупреждение о резком
  изменении давления.

## Установка

```bash
pip install .
```

или в режиме разработки:

```bash
pip install -e .
```

Минимальные зависимости: `requests`, `beautifulsoup4`, `lxml`.

## Использование

```python
from yandex_weather import get_forecast, get_hourly

# Полный прогноз (7 дней + почасовой на сегодня) в виде dict
forecast = get_forecast("Moscow")
print(forecast["city"], len(forecast["days"]), len(forecast["hourly"]))

# Только почасовой прогноз на текущий день
hourly = get_hourly("Moscow")
for slot in hourly["hourly"]:
    print(slot["time"], slot["temperature"], slot["weather_phenomenon"])
```

### Структура возвращаемого `dict` (`get_forecast`)

```python
{
    "city": str,
    "request_date": str,          # ISO-формат
    "days": [
        {
            "date": str,          # ISO-формат
            "magnetic_field": int,
            "magnetic_field_status": str,
            "time_slots": [
                {
                    "time_of_day": str,            # "утром" / "днем" / ...
                    "temperature": int,
                    "perceived_temperature": int | None,
                    "pressure": int,               # мм рт. ст.
                    "humidity": int,               # %
                    "weather_phenomenon": str,
                    "wind_speed": str | None,      # "3 м/с"
                },
                ...
            ],
            "average_daylight_temperature": float | None,
            "pressure_change_warning": str | None,
        },
        ...
    ],
    "hourly": [
        {
            "time": str,                          # "12:00"
            "datetime": str | None,               # ISO-формат (UTC)
            "temperature": int | None,
            "perceived_temperature": int | None,
            "weather_phenomenon": str | None,
            "precipitation_probability": int | None,  # %
            "pressure": int | None,
            "humidity": int | None,
            "wind_speed": str | None,
        },
        ...
    ],
}
```

## Пример

См. `examples/quickstart.py`.

## Структура проекта

```
yandex_weather/
├── __init__.py      # Публичное API: get_forecast(), get_hourly()
├── parser.py        # Парсинг дневного и почасового прогноза
├── processors.py    # Расчёт средней температуры и изменения давления
├── models.py        # Dataclass-модели и to_dict()
├── utils.py         # Вспомогательные функции извлечения данных
└── config.py        # Настройки (URL, таймаут, User-Agent, порог давления)
```

## Конфигурация

Настройки в `yandex_weather/config.py`:

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `YANDEX_WEATHER_BASE_URL` | `"https://yandex.ru/pogoda"` | Базовый URL |
| `REQUEST_TIMEOUT` | `30` | Таймаут HTTP-запросов (сек) |
| `USER_AGENT` | `Mozilla/5.0 ...` | User-Agent для запросов |
| `PRESSURE_CHANGE_THRESHOLD` | `5` | Порог изменения давления (мм рт. ст.) |
