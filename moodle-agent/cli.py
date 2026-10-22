import argparse
import os
from contextlib import nullcontext

from dotenv import load_dotenv

from moodle_agent import notify
from moodle_agent.digest import build_digest
from moodle_agent.moodle import MoodleClient
from moodle_agent.study import collect_material, practice_questions, summarize


def open_client(headless: bool = True):
    """Токен в .env -> Web Services API, иначе браузерная сессия."""
    url, token = os.environ["MOODLE_URL"], os.getenv("MOODLE_TOKEN")
    if token:
        return nullcontext(MoodleClient(url, token))
    from moodle_agent.browser import BrowserClient

    return BrowserClient(url, headless=headless)


def main():
    load_dotenv()
    p = argparse.ArgumentParser(description="Помощник по Moodle")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login", help="войти в Moodle в окне браузера (один раз)")
    d = sub.add_parser("digest", help="сводка дедлайнов")
    d.add_argument("--days", type=int, default=14)
    sub.add_parser("courses", help="список курсов")
    for name in ("summary", "quiz"):
        s = sub.add_parser(name, help="конспект / тренировочные вопросы по курсу")
        s.add_argument("course_id", type=int)
    a = p.parse_args()

    if a.cmd == "login":
        from moodle_agent.browser import BrowserClient

        with BrowserClient(os.environ["MOODLE_URL"], headless=False) as c:
            c.login()
        print("Готово, сессия сохранена.")
        return

    with open_client() as c:
        if a.cmd == "digest":
            notify.send(build_digest(c, a.days))
        elif a.cmd == "courses":
            for x in c.courses():
                print(x["id"], x["fullname"])
        else:
            m = collect_material(c, a.course_id)
            print(summarize(m) if a.cmd == "summary" else practice_questions(m))


if __name__ == "__main__":
    main()
