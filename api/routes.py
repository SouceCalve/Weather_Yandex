from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import logging
from datetime import datetime
from parser.parser import YandexWeatherParser
from parser.processors import WeatherDataProcessor
from parser.excel_generator import ExcelGenerator
from database.db import WeatherDatabase

logger = logging.getLogger(__name__)
router = APIRouter()

parser = YandexWeatherParser()
processor = WeatherDataProcessor()
excel_generator = ExcelGenerator()
db = WeatherDatabase()


@router.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@router.get(
    "/weather",
    response_class=FileResponse,
    tags=["weather"],
    summary="Получить прогноз погоды в формате Excel",
    description="Возвращает Excel файл с прогнозом погоды на 7 дней для указанного города",
)
async def get_weather_excel(
    city: str = Query(..., description="Название города", example="Moscow")
):
    try:
        logger.info(f"Получен запрос на прогноз погоды (Excel) для города: {city}")
        forecast = parser.parse_weather(city)
        forecast.days = processor.process_forecast(forecast.days)
        excel_path = excel_generator.generate(forecast)
        db.save_request(forecast=forecast, status="success")
        filename = (
            f"weather_forecast_{city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        return FileResponse(
            path=str(excel_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
        try:
            db.save_request(forecast=None, status="error", error_message=str(e))
        except Exception as db_error:
            logger.error(f"Ошибка при сохранении в БД: {db_error}")
        raise HTTPException(
            status_code=500, detail=f"Ошибка при получении прогноза погоды: {str(e)}"
        )
