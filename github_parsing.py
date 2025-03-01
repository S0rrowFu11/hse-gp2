import json
import os
import logging
import datetime
from dotenv import load_dotenv
from api import *

parsing_froms = [
    ('ydb-platform', 'ydb'),
    ('ClickHouse', 'ClickHouse'),
    ('catboost', 'catboost')
]
# .env
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

LOGS_LEVEL = os.getenv('LOGS_LEVEL', 'INFO').upper()
for parsing_from in parsing_froms:
    # название репозитория и время запуска
    owner = parsing_from[0]
    repo = parsing_from[1]
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    # настройки логгирования
    log_filename = f'{repo}_log_{timestamp}.log'
    logging.basicConfig(
        filename=log_filename,
        level=getattr(logging, LOGS_LEVEL, logging.INFO),
        format='[%(levelname)s] %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8'
    )
    logger = logging.getLogger()

    # для удобства будем еще дублировать в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s'))
    console_handler.setLevel(getattr(logging, LOGS_LEVEL, logging.INFO))
    logger.addHandler(console_handler)

    if not GITHUB_TOKEN:
        logger.critical('GITHUB_TOKEN не найден в .env!')
        raise ValueError('GITHUB_TOKEN не найден в .env!')

    logger.info(f'Начало парсинга {repo}')
    data = []
    pull_requests = get_all_pull_requests(token=GITHUB_TOKEN, owner=owner, repo=repo)
    for pull_request in pull_requests:
        logging.info(f'Обрабатываем pull_request №{pull_request["number"]}')
        pull_request_details = get_pr_details_data(token=GITHUB_TOKEN, owner=owner, repo=repo,
                                                   pr_num=pull_request["number"])
        reviewers = get_pr_reviewers(token=GITHUB_TOKEN, owner=owner, repo=repo, pr_num=pull_request["number"])
        pull_request_info = {
            'number': pull_request['number'],
            'title': pull_request['title'],
            'user_login': pull_request['user']['login'],
            'created_at': pull_request['created_at'],
            'closed_at': pull_request['closed_at'],
            'merged_at': pull_request_details.get('merged_at'),
            'additions': pull_request_details.get('additions', 0),
            'deletions': pull_request_details.get('deletions', 0),
            'label': [label['name'] for label in pull_request.get('labels', [])],
            'reviewers': reviewers
        }
        data.append(pull_request_info)
    json_filename = f'{repo}_pull_requests_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    contributors = get_contributors(token=GITHUB_TOKEN, owner=owner, repo=repo)
    data = []
    for contributor in contributors:
        user_details = get_user_details(username=contributor['login'], token=GITHUB_TOKEN)
        data.append(user_details)
    json_filename = f'{repo}_contributors_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as f2:
        json.dump(data, f2, ensure_ascii=False, indent=2)
