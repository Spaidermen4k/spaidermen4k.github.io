"""Сводка ближайших дедлайнов."""
from datetime import datetime


def build_digest(client, days: int = 14) -> str:
    events = sorted(client.upcoming(days), key=lambda e: e["timesort"])
    if not events:
        return f"На ближайшие {days} дн. дедлайнов нет."
    lines = [f"Дедлайны на ближайшие {days} дн.:"]
    for e in events:
        when = datetime.fromtimestamp(e["timesort"]).strftime("%d.%m %H:%M")
        course = e.get("course", {}).get("shortname", "")
        lines.append(f"• {when} — {e['name']} [{course}]")
    return "\n".join(lines)
