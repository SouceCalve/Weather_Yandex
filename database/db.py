from datetime import datetime
from pathlib import Path
from typing import Optional
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_PATH
from parser.models import WeatherForecast
from database.models import Base, WeatherRequest

logger = logging.getLogger(__name__)


class WeatherDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"База данных инициализирована: {self.db_path}")

    def _get_session(self):
        return self.Session()

    def save_request(self, forecast: Optional[WeatherForecast], status: str,
                     error_message: Optional[str] = None) -> int:
        session = self._get_session()
        try:
            city = forecast.city if forecast else "unknown"
            request_date = datetime.now()

            weather_request = WeatherRequest(
                city=city,
                request_date=request_date,
                status=status,
                error_message=error_message
            )
            session.add(weather_request)
            session.commit()
            request_id = weather_request.id
            logger.info(f"Запрос сохранен в БД с ID: {request_id}, город: {city}, статус: {status}")
            return request_id
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при сохранении запроса: {e}")
            raise
        finally:
            session.close()

