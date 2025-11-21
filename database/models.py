from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WeatherRequest(Base):
    __tablename__ = 'weather_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False)
    request_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)

