import json
import os
import logging
import datetime
from dotenv import load_dotenv
from api import *

parsing_froms = [
    ('ydb-platform', 'ydb'),
    #('ClickHouse', 'ClickHouse'),
    ('catboost', 'catboost'),
    ('userver-framework', 'userver')
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
    pull_requests_numbers = get_all_pull_requests(token=GITHUB_TOKEN, owner=owner, repo=repo)
    logger.debug(f'Все pull реквесты из {repo} взяты')
    json_filename = f'{repo}_pull_requests_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        f.write("[\n")
        first = True
        for pull_request_number in pull_requests_numbers:
            if not first:
                f.write(",\n")
            first = False
            logging.info(f'Обрабатываем pull_request №{pull_request_number}')
            pull_request_details = get_pr_details_data(token=GITHUB_TOKEN, owner=owner, repo=repo,
                                                       pr_num=pull_request_number)
            reviewers = get_pr_reviewers(token=GITHUB_TOKEN, owner=owner, repo=repo, pr_num=pull_request_number)

            pull_request_info = {
                'number': pull_request_number,
                'title': pull_request_details.get('title', 'Нет названия'),
                'user_login': pull_request_details['user']['login'],
                'created_at': pull_request_details['created_at'],
                'closed_at': pull_request_details.get('closed_at'),
                'merged_at': pull_request_details.get('merged_at'),
                'additions': pull_request_details.get('additions', 0),
                'deletions': pull_request_details.get('deletions', 0),
                'label': [label['name'] for label in pull_request_details.get('labels', [])],
                'reviewers': reviewers
            }
            f.write(json.dumps(pull_request_info, ensure_ascii=False, indent=2))
            logger.debug(f'pull реквест {pull_request_number} записан')
        f.write("\n]")
    contributors = get_contributors(token=GITHUB_TOKEN, owner=owner, repo=repo)
    data = []
    for contributor in contributors:
        user_details = get_user_details(username=contributor['login'], token=GITHUB_TOKEN)
        data.append(user_details)
    json_filename = f'{repo}_contributors_{timestamp}.json'
    with open(json_filename, 'w', encoding='utf-8') as f2:
        json.dump(data, f2, ensure_ascii=False, indent=2)
