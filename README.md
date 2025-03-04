# hse-gp2

# Описание данных

## Общая информация
- **Количество записей:** 16,285
- **Количество столбцов:** 22

## Структура данных

### Основные сведения о Pull Request'ах
- `title`            (строка)   – Заголовок pull request'а.
- `login`            (строка)   – Логин пользователя, создавшего PR.
- `pull_created`     (datetime) – Дата и время создания PR.
- `closed_at`        (datetime) – Дата и время закрытия PR (если закрыт).
- `merged_at`        (datetime) – Дата и время слияния PR (если был смерджен).
- `additions`        (float)    – Количество добавленных строк кода.
- `deletions`        (float)    – Количество удалённых строк кода.
- `labels`           (list)     – Метки, назначенные PR (если есть).
- `reviewers`        (строка)   – Логины пользователей, проверявших PR.
- `source`           (строка)   – Источник данных о пользователе (ydb/userver/catboost).
- `location`         (строка)   – Местоположение пользователя (если указано в профиле).
- `differnce`        (float)    – Разница между датой создания и закрытия PR в днях.
- `platform`         (строка)   – Платформа, откуда получены данные (GitHub/Gitlab).
- `merge_day`        (строка)   – День недели, когда PR был слит (если был).
- `pull_day`         (строка)   – День недели, когда PR был создан.
- `merge_difference` (float)    – Разница во времени между созданием и слиянием PR.
- `files`            (float)    – Количество файлов, затронутых в PR.

### Данные о инициаторе Pull request'а
- `hireable`     (float) – Флаг, доступен ли пользователь для найма (1 – да, 0 – нет, NaN – неизвестно).
- `public_repos` (float) – Количество публичных репозиториев у пользователя.
- `public_gists` (float) – Количество публичных Gist'ов у пользователя.
- `worker_flg`   (int)   – Флаг сотрудника яндекса (1 – сотрудник, 0 – нет).
- `was_reviewer` (float) – Был ли пользователь ревьюером (1 – да, 0 – нет).

### Логика работы с датами создания, закрытия и мерджа:
- `pull_created` есть всегда и он раньше `closed_at` и `merged_at`.
- `merged_at` не моежет быть позже `closed_at`.
- Null значение в `closed_at` означает, что Pull request незакрыт.
- Null значение в `merged_at` означает, что Pull request не был смерджен в ветку.

### Логика работы с остальными полями:
- Null значение означает отсутсвие таких данных как таковых
- В labels в случае отсуствия лейблов хранится пустой `list`
