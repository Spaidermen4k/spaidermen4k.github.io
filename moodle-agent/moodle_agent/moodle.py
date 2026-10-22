"""Тонкий клиент Moodle Web Services (REST)."""
import time

import requests


class MoodleClient:
    def __init__(self, base_url: str, token: str):
        self.endpoint = base_url.rstrip("/") + "/webservice/rest/server.php"
        self.token = token
        self._userid = None

    def call(self, function: str, **params):
        data = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json",
            **params,
        }
        r = requests.post(self.endpoint, data=data, timeout=30)
        r.raise_for_status()
        out = r.json()
        if isinstance(out, dict) and "exception" in out:
            raise RuntimeError(f"{function}: {out.get('message', out)}")
        return out

    @property
    def userid(self) -> int:
        if self._userid is None:
            self._userid = self.call("core_webservice_get_site_info")["userid"]
        return self._userid

    def courses(self):
        return self.call("core_enrol_get_users_courses", userid=self.userid)

    def upcoming(self, days: int = 14):
        """События календаря (дедлайны заданий, тестов) на ближайшие дни."""
        now = int(time.time())
        res = self.call(
            "core_calendar_get_action_events_by_timesort",
            timesortfrom=now,
            timesortto=now + days * 86400,
            limitnum=50,
        )
        return res.get("events", [])

    def course_contents(self, course_id: int):
        return self.call("core_course_get_contents", courseid=course_id)

    def download(self, file_url: str) -> bytes:
        r = requests.get(file_url, params={"token": self.token}, timeout=60)
        r.raise_for_status()
        return r.content
