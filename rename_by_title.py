#!/usr/bin/env python3
from pathlib import Path
import re

DIR = Path(".")  # текущая папка с note-*.md


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:60] or "note"


def main():
    used = set()

    for path in sorted(DIR.glob("note-*.md")):
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = None
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            continue

        base = slugify(title)
        new_name = base
        n = 1
        while new_name in used or (DIR / f"{new_name}.md").exists():
            n += 1
            new_name = f"{base}-{n}"

        used.add(new_name)
        new_path = DIR / f"{new_name}.md"
        print(f"{path.name} -> {new_path.name}")
        path.rename(new_path)


if __name__ == "__main__":
    main()
