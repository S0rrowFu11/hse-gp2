import requests
import logging
import json


def get_request(url: str, headers: dict, params: dict) -> json:
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
    if r.status_code != 200:
        logging.error(f'Ошибка в get запросе: {r.status_code}, {r.text}')
        return None
    return r.json()


def get_all_pull_requests(token: str, owner: str, repo: str) -> list[any]:
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
    params = {'state': 'all', 'per_page': 100, 'page_number': 1}
    header = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    all_pages = []
    page_number = 1
    while True:
        params['page_number'] = page_number
        parsed_pr_page = get_request(url=url, params=params, headers=header)
        if not parsed_pr_page:
            logging.debug(f'Страница с pull requests пустая')
            break
        all_pages.extend(parsed_pr_page)
        page_number += 1
        logging.info(f'Получено {len(all_pages)} pull request\'ов')
    return all_pages


def get_pr_details_data(token: str, owner: str, repo: str, pr_num: int):
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
    logging.debug('Запрос на детальную информацию по pr')
    return get_request(url=url, headers=header)


def grt_pr_reviewers(token: str, owner: str, repo: str, pr_num: int):
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
    return get_request(url=url, headers=header)
