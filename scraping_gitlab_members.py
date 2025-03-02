import os
import datetime
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
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

# настройки
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 2)

account_links = []
page = 1
base_url = 'https://gitlab.com/gitlab-org/gitlab/-/project_members'

while True:
    url = f'https://gitlab.com/gitlab-org/gitlab/-/project_members?page={page}'
    driver.get(url)
    logger.info(f'открываем страницу: {url}')
    try:
        # ожидание загрузки
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.js-user-link')))
    except Exception as e:
        logger.critical('на странице ничего нет')
        break
    # берем ссылки на аккаунты
    members = driver.find_elements(By.CSS_SELECTOR, 'a.js-user-link')
    if not members:
        logger.info(f'на странице {page} участников не найдено, завершаем цикл.')
        break
    for member in members:
        account_links.append(member.get_attribute("href"))
    logger.debug(f'страница {page} обработана, всего найдено ссылок: {len(account_links)}')
    page += 1
    time.sleep(3)  # задержка, чтобы не уйти в бан
driver.quit()

df = pd.DataFrame(account_links, columns=['members_links'])
df.to_csv('account_links.csv', index=False)
logger.info('файл сохранен')
