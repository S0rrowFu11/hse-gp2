import requests
import logging
import json
import time



def get_request(url: str, headers: dict, **kwargs) -> json:
    params = kwargs.get("params", None)
    if not url:
        logging.critical('Нет url')
        TypeError('Нет url')
    if not headers:
        logging.critical('Нет headers')
        TypeError('Нет headers')
    if not params:
        logging.info('Нет params')
        r = requests.get(url, headers=headers)
    else:
        r = requests.get(url, headers=headers, params=params)
    if r.status_code == 403:
        reset_time = int(r.headers.get('X-RateLimit-Reset', time.time() + 60))
        sleep_duration = max(0, reset_time - time.time()) + 5  # Добавляем 5 секунд для надежности
        logging.warning(f'Превышен лимит запросов. Ожидание {sleep_duration} секунд до сброса лимита.')
        time.sleep(sleep_duration)
        return get_request(url, headers, **kwargs)
    if r.status_code != 200:
        logging.error(f'Ошибка в get запросе: {r.status_code}, {r.text}')
        return None
    return r.json()


def get_all_pull_requests(token: str, owner: str, repo: str) -> list[any]:
    logging.info(f"Берем все пул реквесты")
    if not token:
        logging.critical('Нет token')
        TypeError('Нет token')
    if not owner:
        logging.critical('Нет owner')
        TypeError('Нет owner')
    if not repo:
        logging.critical('Нет repo')
        TypeError('Нет repo')
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    params = {'state': 'all', 'per_page': 100, 'page': 1}
    header = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    pull_requests_numbers = []
    page_number = 1
    while True:
        params['page'] = page_number
        parsed_pr_page = get_request(url=url, headers=header, params=params)
        if not parsed_pr_page:
            logging.debug(f'Страница с pull requests пустая')
            break
        for pull_request in parsed_pr_page:
            pull_requests_numbers.append(pull_request['number'])
        page_number += 1
        logging.info(f'Получено {len(pull_requests_numbers)} pull request\'ов')
    return pull_requests_numbers


def get_pr_details_data(token: str, owner: str, repo: str, pr_num: int):
    logging.info(f"Берем информацию о {pr_num} реквесте")
    if not token:
        logging.critical('Нет token')
        TypeError('Нет token')
    if not owner:
        logging.critical('Нет owner')
        TypeError('Нет owner')
    if not repo:
        logging.critical('Нет repo')
        TypeError('Нет repo')
    if not pr_num:
        logging.critical('Нет pr_num')
        TypeError('Нет pr_num')
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}"
    header = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    logging.debug(f'Запрос на детальную информацию по pr {pr_num}')
    return get_request(url=url, headers=header)


def get_pr_reviewers(token: str, owner: str, repo: str, pr_num: int):
    if not token:
        logging.critical('Нет token')
        TypeError('Нет token')
    if not owner:
        logging.critical('Нет owner')
        TypeError('Нет owner')
    if not repo:
        logging.critical('Нет repo')
        TypeError('Нет repo')
    if not pr_num:
        logging.critical('Нет pr_num')
        TypeError('Нет pr_num')
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/reviews"
    header = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    logging.debug(f'Запрос на ревьюеров pr {pr_num}')
    reviewers = get_request(url=url, headers=header)
    reviewers_usernames = []
    for reviewer in reviewers:
        reviewers_usernames.append(reviewer['user']['login'])
    return reviewers_usernames


def get_contributors(token: str, owner: str, repo: str):
    if not token:
        logging.critical('Нет token')
        TypeError('Нет token')
    if not owner:
        logging.critical('Нет owner')
        TypeError('Нет owner')
    if not repo:
        logging.critical('Нет repo')
        TypeError('Нет repo')
    logging.info(f"Берем контрибьюторов {repo}")
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    header = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    contributors = []
    per_page = 100
    page = 1
    while True:
        params = {'per_page': per_page, 'page': page}
        data = get_request(url=url, headers=header, params=params)
        if not data:
            break
        contributors.extend(data)
        if len(data) < per_page:
            break
        page += 1
    return contributors


def get_user_details(username: str, token: str):
    if not token:
        logging.critical('Нет token')
        TypeError('Нет token')
    if not username:
        logging.critical('Нет username')
        TypeError('Нет username')
    logging.info(f"Берем детальную информацию о {username}")
    url = f"https://api.github.com/users/{username}"
    header = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    return get_request(url=url, headers=header)
