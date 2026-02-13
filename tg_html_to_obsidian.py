#!/usr/bin/env python3
import json
from pathlib import Path

import bs4
import requests

# === НАСТРОЙКИ ===

HTML_PATH = "messages2.html"  # имя html-файла экспорта
OUT_DIR = Path("/Users/YOURNAME/Desktop/Obsidian")  # папка в вольте
MODEL_NAME = "llama3.2:3b"

MIN_LEN = 300  # отбрасываем сообщения короче N символов

OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE = """Ты конвертер постов из Telegram в заметки Obsidian.

Формат ответа строго такой Markdown:

# Краткий заголовок
Теги: #tag1 #tag2 #tag3

Основной текст заметки

Никаких объяснений, шагов, комментариев, списков действий и т.п.
Только готовый Markdown, как в примере выше.

Вот текст поста:
{post}
"""


def load_messages(path: str):
    with open(path, "r", encoding="utf-8") as f:
        soup = bs4.BeautifulSoup(f, "html.parser")

    for msg in soup.select("div.message"):
        body = msg.select_one("div.body")
        if not body:
            continue

        text_div = body.select_one("div.text")
        if not text_div:
            continue

        text = text_div.get_text("\n", strip=True)
        if not text.strip():
            continue

        if len(text) < MIN_LEN:
            continue

        yield text


def to_obsidian_note(post_text: str) -> str:
    prompt = PROMPT_TEMPLATE.format(post=post_text)

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
    return "".join(chunks)


def main():
    print("Читаю HTML из:", HTML_PATH)
    print("Пишу заметки в:", OUT_DIR)
    count = 0

    for i, text in enumerate(load_messages(HTML_PATH), start=1):
        print(f"\n=== Сообщение #{i} (len={len(text)}) ===")
        try:
            md = to_obsidian_note(text)
        except Exception as e:
            print("!! Ошибка при обращении к модели:", repr(e))
            continue

        fname = OUT_DIR / f"note-{i:04d}.md"
        try:
            fname.write_text(md, encoding="utf-8")
            print("✓ Сохранено:", fname)
            count += 1
        except Exception as e:
            print("!! Ошибка при записи файла:", repr(e))

    print(f"\nГотово. Создано файлов: {count}")


if __name__ == "__main__":
    main()
