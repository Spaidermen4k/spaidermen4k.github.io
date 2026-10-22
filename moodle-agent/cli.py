import argparse
import os

from dotenv import load_dotenv

from moodle_agent import notify
from moodle_agent.digest import build_digest
from moodle_agent.moodle import MoodleClient
from moodle_agent.study import collect_material, practice_questions, summarize


def main():
    load_dotenv()
    p = argparse.ArgumentParser(description="Помощник по Moodle")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("digest", help="сводка дедлайнов")
    d.add_argument("--days", type=int, default=14)
    sub.add_parser("courses", help="список курсов")
    for name in ("summary", "quiz"):
        s = sub.add_parser(name, help="конспект / тренировочные вопросы по курсу")
        s.add_argument("course_id", type=int)
    a = p.parse_args()

    c = MoodleClient(os.environ["MOODLE_URL"], os.environ["MOODLE_TOKEN"])
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
