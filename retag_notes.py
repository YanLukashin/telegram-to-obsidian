#!/usr/bin/env python3
from pathlib import Path
import json
import textwrap
import requests

VAULT_DIR = Path(".")  # текущая папка с .md
MODEL_NAME = "llama3.2:3b"

ALLOWED_TAGS = [
    "#ai", "#obsidian", "#productivity", "#crypto", "#trading",
    "#education", "#mindset", "#dev", "#business",
    "#thread", "#note", "#guide",
]

PROMPT_TEMPLATE = textwrap.dedent("""
Ты помогаешь расставлять теги в Obsidian.

Тебе даётся содержимое заметки в Markdown.

У тебя есть только такие допустимые теги:
{allowed}

Выбери от 2 до 6 тегов из этого списка, которые лучше всего описывают заметку.
Верни ОДНУ строку строго в формате:

Теги: #tag1 #tag2 #tag3

Никаких других строк, комментариев и объяснений.

Вот текст заметки:
{note}
""").strip()


def get_new_tags(md_text: str) -> str:
    prompt = PROMPT_TEMPLATE.format(
        allowed=" ".join(ALLOWED_TAGS),
        note=md_text,
    )
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": MODEL_NAME, "prompt": prompt},
        stream=True,
        timeout=600,
    )
    resp.raise_for_status()

    chunks = []
    for line in resp.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        chunks.append(data.get("response", ""))
        if data.get("done"):
            break
    line = "".join(chunks).strip()
    # на всякий случай оставим только первую строку
    return line.splitlines()[0]


def process_file(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # ищем строку с "Теги:"
    tag_idx = None
    for i, line in enumerate(lines):
        if line.lower().startswith("теги:"):
            tag_idx = i
            break

    new_tag_line = get_new_tags(text)
    print(f"{path.name}: {new_tag_line}")

    if tag_idx is not None:
        lines[tag_idx] = new_tag_line
    else:
        # вставим после заголовка, если его нет
        insert_at = 1
        if lines and not lines[0].startswith("# "):
            insert_at = 0
        lines.insert(insert_at, new_tag_line)

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    for path in sorted(VAULT_DIR.glob("*.md")):
        process_file(path)


if __name__ == "__main__":
    main()
