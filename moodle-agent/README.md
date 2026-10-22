# Moodle-помощник

Следит за дедлайнами, делает конспекты и тренировочные вопросы по материалам курсов.
Задания и тесты **не** выполняет и не сдаёт — это делаешь ты.

## Запуск
    pip install -r requirements.txt
    cp .env.example .env   # заполни MOODLE_URL и MOODLE_TOKEN
    python cli.py courses
    python cli.py digest --days 7
    python cli.py summary <course_id>
    python cli.py quiz <course_id>

## Токен Moodle
Профиль → Настройки → Security keys → «Moodle mobile web service». Если пункта нет,
веб-сервисы отключены — напиши, добавим вход через браузер (Playwright).

Для ежедневной сводки добавь `python cli.py digest` в cron.
