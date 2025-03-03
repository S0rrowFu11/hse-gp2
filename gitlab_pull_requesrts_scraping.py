import datetime
import os
import random
import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
from dotenv import load_dotenv

# .env
load_dotenv()
LOGS_LEVEL = os.getenv('LOGS_LEVEL', 'INFO').upper()
# логгирование
logger = logging.getLogger()
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
log_filename = f'gitlab_log_{timestamp}.log'
logging.basicConfig(
    filename=log_filename,
    level=getattr(logging, LOGS_LEVEL, logging.INFO),
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

logger.debug('считываем файл merge_request_links.csv')
links_df = pd.read_csv("merge_request_links.csv")
merge_request_links = links_df["merge_request_links"].tolist()

logger.debug('создаем output файл')
output_file = open("merge_requests_details.jsonl", "a", encoding="utf-8")

logger.info('начинаем парсить')
for link in merge_request_links:
    data = {"url": link}
    logger.debug(f'открываем сайт {link}')
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 8)
    try:
        driver.get(link)
        time.sleep(3)  # ждем загрузку страницы
    except Exception as e:
        logger.warning(f"ошибка загрузки {link}: {e}")
        driver.quit()
        output_file.write(json.dumps(data, ensure_ascii=False) + "\n")
        continue

    logger.info('берем логин пользователя-инициатора')
    try:
        author_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@data-testid='author-link']")))
        author_href = author_element.get_attribute("href")
        if author_href.startswith("http"):
            author_username = author_href.rstrip("/").split("/")[-1]
        else:
            author_username = author_href.lstrip("/")
        data["author"] = author_username
    except Exception as e:
        print(f"Ошибка при извлечении автора для {link}: {e}")
        data["author"] = None

    logger.info('берем дату создания')
    try:
        created_date_element = driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'detail-page-description') and contains(@class, 'is-merge-request')]//time")
        data["created_at"] = created_date_element.get_attribute("datetime")
    except Exception as e:
        print(f"Ошибка при извлечении даты создания для {link}: {e}")
        data["created_at"] = None

    logger.info('берем дату мерджа')
    try:
        merge_time_element = driver.find_element(By.XPATH,
                                                 "//div[contains(@class, 'note-header-info')]//span[contains(text(),'merged')]/following::time[1]")
        data["merged_at"] = merge_time_element.get_attribute("datetime")
    except Exception as e:
        data["merged_at"] = None

    logger.info('берем дату закрытия')
    try:
        closed_time_element = driver.find_element(By.XPATH,
                                                  "//div[contains(@class, 'note-header-info')]//span[contains(text(),'closed')]/following::time[1]")
        data["closed_at"] = closed_time_element.get_attribute("datetime")
    except Exception as e:
        data["closed_at"] = None


    logger.info(f"обработан {link}")
    output_file.write(json.dumps(data, ensure_ascii=False) + "\n")
    output_file.flush()
    logger.info('данные записаны в файл')
    driver.quit()

    # генерация рандомного поведения для обмана анти-робота
    random_ver = random.randint(1, 10)
    if random_ver >= 8:
        time.sleep(5 + random.randint(100, 240))
    if random_ver <= 5:
        time.sleep(5 + random.randint(10, 40))
    else:
        time.sleep(5 + random.randint(1, 10))

output_file.close()
logger.info("Данные успешно сохранены")
