import requests
import logging
import json


def get_request(url: str, headers: dict, params: dict) -> json:
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        logging.error(f'Ошибка в get запросе: {r.status_code}, {r.text}')
        return None
    return r.json()


def get_all_pull_requests(token: str, owner: str, repo: str) -> list[any]:
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
