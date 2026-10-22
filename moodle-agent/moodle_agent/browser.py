"""Клиент Moodle через браузерную сессию (Playwright).

Вход делает человек в настоящем окне (логин, SSO, 2FA), сессия лежит в профиле
браузера. Данные берём через тот же внутренний AJAX-сервис, что использует сам
сайт Moodle, поэтому формат ответов совпадает с Web Services API.
"""
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".moodle-agent" / "profile"


class BrowserClient:
    def __init__(self, base_url: str, headless: bool = True):
        self.base = base_url.rstrip("/")
        self.headless = headless
        self._pw = self._ctx = self._page = None
        self._sesskey = self._userid = None

    def __enter__(self):
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        self._pw = sync_playwright().start()
        self._ctx = self._pw.chromium.launch_persistent_context(
            str(PROFILE_DIR), headless=self.headless
        )
        self._page = self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()
        return self

    def __exit__(self, *exc):
        self._ctx.close()
        self._pw.stop()

    def login(self):
        """Открыть окно, дождаться ручного входа."""
        self._page.goto(f"{self.base}/login/index.php")
        input("Войди в Moodle в открывшемся окне, затем нажми Enter здесь... ")
        self._load_session()

    def _load_session(self):
        self._page.goto(f"{self.base}/my/")
        if "/login/" in self._page.url:
            raise RuntimeError("Сессия не найдена или истекла. Запусти: python cli.py login")
        cfg = self._page.evaluate("({k: M.cfg.sesskey, u: M.cfg.userId})")
        self._sesskey, self._userid = cfg["k"], cfg["u"]

    def call(self, function: str, **args):
        if self._sesskey is None:
            self._load_session()
        r = self._ctx.request.post(
            f"{self.base}/lib/ajax/service.php?sesskey={self._sesskey}&info={function}",
            data=[{"index": 0, "methodname": function, "args": args}],
        )
        item = r.json()[0]
        if item.get("error"):
            raise RuntimeError(f"{function}: {item['exception'].get('message')}")
        return item["data"]

    @property
    def userid(self) -> int:
        if self._userid is None:
            self._load_session()
        return self._userid

    def courses(self):
        data = self.call(
            "core_course_get_enrolled_courses_by_timeline_classification",
            classification="inprogress", limit=0, offset=0, sort="fullname",
        )
        return data["courses"]

    def upcoming(self, days: int = 14):
        import time

        now = int(time.time())
        data = self.call(
            "core_calendar_get_action_events_by_timesort",
            timesortfrom=now, timesortto=now + days * 86400, limitnum=50,
        )
        return data.get("events", [])

    def course_pdfs(self, course_id: int):
        """[(название, байты PDF)] со страницы курса."""
        self._page.goto(f"{self.base}/course/view.php?id={course_id}")
        links = self._page.eval_on_selector_all(
            'a[href*="/mod/resource/view.php"], a[href*="pluginfile.php"]',
            "els => els.map(e => [e.textContent.trim(), e.href])",
        )
        out, seen = [], set()
        for name, href in links:
            if href in seen:
                continue
            seen.add(href)
            resp = self._ctx.request.get(href)
            if resp.ok and "pdf" in resp.headers.get("content-type", ""):
                out.append((re.sub(r"\s+", " ", name), resp.body()))
        return out
