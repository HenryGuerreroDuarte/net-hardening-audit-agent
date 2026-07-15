def parse_stat(text: str) -> dict[str, dict[str, str]]:
    """Parse `stat -c '%n %a %U %G'` output into {path: {mode, owner, group}}."""
    results = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        path, mode, owner, group = parts
        results[path] = {"mode": mode, "owner": owner, "group": group}
    return results
