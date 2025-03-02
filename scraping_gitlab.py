from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# настройки
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 2)

account_links = []
page = 1
base_url = "https://gitlab.com/gitlab-org/gitlab/-/project_members"

while True:
    url = f"{base_url}?page={page}"
    driver.get(url)
    print(f"Открываем страницу: {url}")
    try:
        # ожидание загрузки
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.js-user-link")))
    except Exception as e:
        break
    # берем ссылки на аккаунты
    members = driver.find_elements(By.CSS_SELECTOR, "a.js-user-link")
    if not members:
        print(f"На странице {page} участников не найдено, завершаем цикл.")
        break
    for member in members:
        account_links.append(member.get_attribute("href"))
    print(f"Страница {page} обработана, всего найдено ссылок: {len(account_links)}")
    page += 1
    time.sleep(2)  # задержка, чтобы не уйти в бан
driver.quit()
