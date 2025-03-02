import datetime
import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import random
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
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(20)
wait = WebDriverWait(driver, 20)

start_url = "https://gitlab.com/gitlab-org/gitlab/-/merge_requests/?sort=created_date&state=all"

# берем только нужные для нас ссылки, маска регулярного выражения:
reg = re.compile(r'/-/merge_requests/\d+($|\?)')
pages = 1
mr_links = []
while True:
    # берем только первые 250 страниц
    if pages >= 250:
        break
    pages += 1
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href, '/-/merge_requests/') and contains(@class, 'gl-link')]")
        ))
    except TimeoutException as e:
        logger.critical(f'ничего не удалось найти, {e}')
        break
    links = driver.find_elements(By.XPATH, "//a[contains(@href, '/-/merge_requests/') and contains(@class, 'gl-link')]")
    count_before = len(mr_links)
    for link in links:
        href = link.get_attribute("href")
        if href and reg.search(href) and href not in mr_links:
            mr_links.append(href)
    count_after = len(mr_links)
    logging.info(f"обработано: добавлено {count_after - count_before} ссылок, всего {len(mr_links)} ссылок.")
    try:
        next_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='nextButton']")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        next_button.click()
        # рандомный слип, чтобы запутать gitlab
        time.sleep(5 + random.randint(1, 10))
    except Exception as e:
        logging.warning("кнопка Next не найдена или недоступна", e)
        break

driver.quit()

# сохраняем в файл
df = pd.DataFrame(mr_links, columns=["merge_request_links"])
df.to_csv("merge_request_links.csv", index=False)
logging.info("CSV файл сохранён")
