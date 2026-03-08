import re

import django
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver


def _sample_value(converter: str, name: str) -> str:
    converter = (converter or "str").lower()
    if converter == "int":
        return "1"
    if converter == "slug":
        return "sample-slug"
    if converter == "uuid":
        return "00000000-0000-0000-0000-000000000001"
    if converter == "path":
        return "sample/path"
    if "token" in name.lower():
        return "00000000-0000-0000-0000-000000000001"
    if name.lower().endswith("id") or name.lower() in {"pk", "id"}:
        return "1"
    return "sample"


def _materialize_path(route: str) -> str:
    route = route.replace("^", "").replace("$", "")
    # Replace path converters: <int:pk>, <slug:name>, <uuid:token>, <path:file>
    def repl(match):
        conv = match.group(1) or "str"
        name = match.group(2)
        return _sample_value(conv, name)

    route = re.sub(r"<(?:(\w+):)?(\w+)>", repl, route)

    # Skip regex-style unresolved patterns
    if "(?P<" in route or "[" in route or "(" in route:
        return ""

    route = route.lstrip("/")
    if route and not route.endswith("/"):
        route += "/"
    return "/" + route


def _collect_patterns(patterns, prefix=""):
    collected = []
    for p in patterns:
        if isinstance(p, URLResolver):
            new_prefix = prefix + str(p.pattern)
            collected.extend(_collect_patterns(p.url_patterns, new_prefix))
        elif isinstance(p, URLPattern):
            full_route = prefix + str(p.pattern)
            collected.append((full_route, p.name or ""))
    return collected


def main():
    django.setup()

    resolver = get_resolver()
    patterns = _collect_patterns(resolver.url_patterns)

    # Deduplicate while preserving order
    seen = set()
    routes = []
    for route, name in patterns:
        key = (route, name)
        if key not in seen:
            seen.add(key)
            routes.append((route, name))

    anon = Client()

    user = None
    try:
        from apps.users.models import User

        user = User.objects.filter(is_active=True).first()
    except Exception:
        user = None

    rows = []
    for raw_route, name in routes:
        path = _materialize_path(raw_route)
        if not path:
            continue

        try:
            a = anon.get(path, HTTP_HOST="127.0.0.1")
            anon_code = a.status_code
        except Exception as exc:
            anon_code = f"ERR:{type(exc).__name__}"

        try:
            if user:
                auth = Client()
                auth.force_login(user)
                b = auth.get(path, HTTP_HOST="127.0.0.1")
                auth_code = b.status_code
            else:
                auth_code = "NO_USER"
        except Exception as exc:
            auth_code = f"ERR:{type(exc).__name__}"

        rows.append((path, name, anon_code, auth_code))

    total = len(rows)
    broken_anon = [r for r in rows if isinstance(r[2], int) and r[2] >= 500]
    broken_auth = [r for r in rows if isinstance(r[3], int) and r[3] >= 500]

    print(f"Total tested routes: {total}")
    print(f"Auth test user: {'yes' if user else 'no'}")
    print(f"Anon 5xx: {len(broken_anon)}")
    print(f"Auth 5xx: {len(broken_auth)}")

    print("\n--- FAILURES (5xx) ---")
    for path, name, anon_code, auth_code in rows:
        fail_anon = isinstance(anon_code, int) and anon_code >= 500
        fail_auth = isinstance(auth_code, int) and auth_code >= 500
        if fail_anon or fail_auth:
            print(f"{path} | name={name or '-'} | anon={anon_code} | auth={auth_code}")

    print("\n--- ROUTE STATUS MATRIX ---")
    for path, name, anon_code, auth_code in rows:
        print(f"{path} | name={name or '-'} | anon={anon_code} | auth={auth_code}")


if __name__ == "__main__":
    main()
