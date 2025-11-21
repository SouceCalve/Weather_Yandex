import sys
import argparse
import logging
from parser.parser import YandexWeatherParser
from parser.processors import WeatherDataProcessor
from parser.excel_generator import ExcelGenerator
from database.db import WeatherDatabase
from api.app import run_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("weather_parser.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main_cli(city: str, open_excel: bool = True):
    try:
        logger.info(f"Начало работы парсера погоды для города: {city}")
        parser = YandexWeatherParser()
        processor = WeatherDataProcessor()
        excel_generator = ExcelGenerator()
        db = WeatherDatabase()
        logger.info("Получение данных с Яндекс.Погоды...")
        forecast = parser.parse_weather(city)
        logger.info("Обработка данных...")
        forecast.days = processor.process_forecast(forecast.days)
        logger.info("Генерация Excel файла...")
        excel_path = excel_generator.generate(forecast)
        logger.info("Сохранение данных в базу данных...")
        request_id = db.save_request(forecast=forecast, status="success")
        logger.info(f"Успешно! Запрос сохранен с ID: {request_id}")
        logger.info(f"Excel файл создан: {excel_path}")
        if open_excel:
            logger.info("Открытие Excel файла...")
            excel_generator.open_file(excel_path)
        return 0
    except Exception as e:
        logger.error(f"Ошибка при выполнении: {e}", exc_info=True)
        try:
            db = WeatherDatabase()
            db.save_request(forecast=None, status="error", error_message=str(e))
        except Exception as db_error:
            logger.error(f"Ошибка при сохранении в БД: {db_error}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Парсер погоды с Яндекс.Погоды",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "city", nargs="?", help="Название города для получения прогноза погоды"
    )
    parser.add_argument(
        "--web-service",
        action="store_true",
        help="Запустить веб-сервис вместо CLI режима",
    )
    parser.add_argument(
        "--host", type=str, help="Хост для веб-сервиса (по умолчанию из config)"
    )
    parser.add_argument(
        "--port", type=int, help="Порт для веб-сервиса (по умолчанию из config)"
    )
    parser.add_argument(
        "--no-open", action="store_true", help="Не открывать Excel файл после создания"
    )
    args = parser.parse_args()
    if args.web_service:
        logger.info("Запуск в режиме веб-сервиса")
        run_server(host=args.host, port=args.port)
        return 0
    if not args.city:
        parser.error(
            "Необходимо указать название города или использовать --web-service"
        )
    return main_cli(args.city, open_excel=not args.no_open)


if __name__ == "__main__":
    sys.exit(main())
