# Moodle-помощник

Следит за дедлайнами, делает конспекты и тренировочные вопросы по материалам курсов.
Задания и тесты **не** выполняет и не сдаёт — это делаешь ты.

## Запуск (вход через браузер)
    pip install -r requirements.txt
    playwright install chromium
    cp .env.example .env   # заполни MOODLE_URL; MOODLE_TOKEN оставь пустым
    python cli.py login    # откроется окно: войди сам (логин/SSO/2FA), нажми Enter
    python cli.py courses
    python cli.py digest --days 7
    python cli.py summary <course_id>
    python cli.py quiz <course_id>

Пароль агент не видит: сессия хранится в профиле браузера `~/.moodle-agent/profile`.
Когда сессия истечёт — снова `python cli.py login`.
Если есть токен Moodle (MOODLE_TOKEN в .env), используется официальный API без браузера.
Запускать нужно на своём компьютере — вход в окне невозможен в облачном контейнере.

Для ежедневной сводки добавь `python cli.py digest` в cron.
