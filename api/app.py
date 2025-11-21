from fastapi import FastAPI
import logging
import uvicorn
from config import WEB_SERVICE_HOST, WEB_SERVICE_PORT
from api.routes import router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Парсер погоды Яндекс.Погоды",
    description="API для получения прогноза погоды на 7 дней",
    version="1.0.0",
)

app.include_router(router)


def run_server(host: str = None, port: int = None):
    host = host or WEB_SERVICE_HOST
    port = port or WEB_SERVICE_PORT
    logger.info(f"Запуск веб-сервиса на {host}:{port}")
    uvicorn.run("api.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run_server()
