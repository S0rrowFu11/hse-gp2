import os
import logging
import datetime
from dotenv import load_dotenv


# название репозитория и время запуска
repo_name = "ydb-platform_ydb"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# настройки логгирования
log_filename = f"{repo_name}_log_{timestamp}.log"
json_filename = f"{repo_name}_pull_requests_{timestamp}.json"
logging.basicConfig(
    filename=log_filename,
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)
logger = logging.getLogger()

# для удобства будем еще дублировать в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logger.addHandler(console_handler)

if not GITHUB_TOKEN:
    logger.critical("GITHUB_TOKEN не найден в .env!")
    raise ValueError("GITHUB_TOKEN не найден в .env!")

logger.info("Начало парсинга")


