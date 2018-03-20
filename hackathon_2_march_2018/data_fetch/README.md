# Код для экспорта данных из JSON-дампа Slack в БД

Получает данные про 
- пользователей (таблица imported_user_data)
- каналы (таблица imported_channel)
- сообщения (таблица imported_messages)
- реакции на сообщения по юзерам (таблица imported_reactions)
- количество реакций на сообщения по типам (таблица imported_reactions_count) 

# Prerequisites

```
python3 -m pip install -r requirements.txt
```

# Usage

```
python3 run.py
```

Предполагается, что в ../data лежат разархивированный ODS-дамп.

База (по умолчанию sqlite) будет лежать в ../ods-slack.db. 

# Notes

- В imported_reactions не все юзеры, т.к. в дампе указаны не все юзеры, поставившие смайл.<br/>
  Дамп отображает on-hover поведение Slack: показывает ~50 именованных юзеров, а дальше пишет and 42 others.<br/>
  Вот эти 42 юзера не попали в дамп.
