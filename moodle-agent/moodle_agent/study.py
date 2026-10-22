"""Конспекты и тренировочные вопросы по материалам курса (для подготовки)."""
import io

import anthropic
from pypdf import PdfReader

MODEL = "claude-sonnet-5-5"


def _pdf_text(raw: bytes, limit: int = 60000) -> str:
    reader = PdfReader(io.BytesIO(raw))
    return "\n".join(p.extract_text() or "" for p in reader.pages)[:limit]


def collect_material(client, course_id: int) -> str:
    chunks = []
    for section in client.course_contents(course_id):
        for module in section.get("modules", []):
            for f in module.get("contents", []):
                if f.get("filename", "").lower().endswith(".pdf"):
                    chunks.append(f"# {module['name']}\n{_pdf_text(client.download(f['fileurl']))}")
    return "\n\n".join(chunks)


def _ask(prompt: str, material: str) -> str:
    msg = anthropic.Anthropic().messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": f"{prompt}\n\n<material>\n{material}\n</material>"}],
    )
    return msg.content[0].text


def summarize(material: str) -> str:
    return _ask("Сделай структурированный конспект на русском: ключевые понятия, формулы, выводы.", material)


def practice_questions(material: str, n: int = 10) -> str:
    return _ask(
        f"Составь {n} тренировочных вопросов для самопроверки по этому материалу, "
        "а в конце дай краткие ответы отдельным блоком.",
        material,
    )
