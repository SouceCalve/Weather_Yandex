from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "weather_data.db"
EXCEL_OUTPUT_DIR = BASE_DIR / "output"

EXCEL_OUTPUT_DIR.mkdir(exist_ok=True)

YANDEX_WEATHER_BASE_URL = "https://yandex.ru/pogoda"

REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

PRESSURE_CHANGE_THRESHOLD = 5

WEB_SERVICE_HOST = "0.0.0.0"
WEB_SERVICE_PORT = 5000
