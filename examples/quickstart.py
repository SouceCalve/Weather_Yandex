from yandex_weather import get_forecast, get_hourly


def main():
    city = "novosibirsk"

    forecast = get_forecast(city)
    print(f"Прогноз для города: {forecast['city']}")
    print(f"Дней в прогнозе: {len(forecast['days'])}")
    print(f"Почасовых слотов: {len(forecast['hourly'])}")

    print("\nПервый день:")
    day = forecast["days"][0]
    print(f"  Дата: {day['date']}, магнитное поле: {day['magnetic_field']}")
    for slot in day["time_slots"]:
        print(
            f"  {slot['time_of_day']}: {slot['temperature']}°C, "
            f"{slot['weather_phenomenon']}, давление {slot['pressure']} мм"
        )

    print("\nПочасовой прогноз (первые 3 слота):")
    for slot in forecast["hourly"][:11]:
        print(
            f"  {slot['time']}: {slot['temperature']}°C, "
            f"{slot['weather_phenomenon']}, осадки {slot['precipitation_probability']}%"
        )

    hourly = get_hourly(city)
    print(f"\nТолько почасовой (через get_hourly): {len(hourly['hourly'])} слотов")


if __name__ == "__main__":
    main()
