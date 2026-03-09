import re
from pathlib import Path
import django
import os
import sys
from django.urls import get_resolver

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

TEMPLATE_DIR = Path("templates")
URL_RE = re.compile(r"\{\%\s*url\s+['\"]([^'\"]+)['\"]")


def name_exists(url_name: str, resolver) -> bool:
    if ":" not in url_name:
        return url_name in resolver.reverse_dict

    parts = url_name.split(":")
    current = resolver
    for ns in parts[:-1]:
        if ns not in current.namespace_dict:
            return False
        _, current = current.namespace_dict[ns]
    return parts[-1] in current.reverse_dict


def main() -> int:
    resolver = get_resolver()
    missing = []

    for path in TEMPLATE_DIR.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for idx, line in enumerate(text.splitlines(), start=1):
            for match in URL_RE.finditer(line):
                name = match.group(1)
                if not name_exists(name, resolver):
                    missing.append((str(path), idx, name))

    if not missing:
        print("OK: No unresolved template URL names found.")
        return 0

    print("MISSING TEMPLATE URL NAMES:")
    for p, line, n in missing:
        print(f"{p}:{line} -> {n}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
