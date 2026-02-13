Опорный каркас:

text
# Telegram → Obsidian Converter

Скрипты, которые превращают экспорт Telegram-канала в структурированный Obsidian-вольт: одна заметка на пост, нормальные заголовки и теги.

## Возможности

- Парсинг HTML-экспорта Telegram Desktop.
- Фильтрация коротких сообщений (по длине текста).
- Генерация заметок через локальную LLM (Ollama + llama3.2:3b).
- Переименование файлов по заголовкам заметок.
- Ретегинг заметок по словарю тегов.

## Быстрый старт

```bash
git clone https://github.com/you/telegram-to-obsidian.git
cd telegram-to-obsidian

python3 -m pip install --user beautifulsoup4 requests
Установи и запусти Ollama, скачай модель:

bash
ollama serve
ollama pull llama3.2:3b
Сделай HTML-экспорт канала из Telegram.

Положи messages.html и src/tg_html_to_obsidian.py в одну папку.

В tg_html_to_obsidian.py пропиши путь к своему Obsidian-вольту.

Запусти:

bash
python3 tg_html_to_obsidian.py
В папке вольта:

bash
python3 src/rename_by_title.py
python3 src/retag_notes.py   # опционально, для тегов
Конфигурация
OUT_DIR — путь к папке в Obsidian.

MIN_LEN — минимальная длина сообщения.

ALLOWED_TAGS в retag_notes.py — твой словарь тегов.
