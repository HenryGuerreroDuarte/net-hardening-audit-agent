def parse_sshd_effective(text: str) -> dict[str, str | list[str]]:
    """Parse `sshd -T` output: one 'key value' pair per line, keys lowercase.
    Some keys repeat (hostkey, ciphers can appear multiple times) — those
    become lists so no data is silently dropped."""
    settings: dict[str, str | list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        key, _, value = line.partition(" ")
        key = key.lower()
        if key in settings:
            prev = settings[key]
            settings[key] = prev + [value] if isinstance(prev, list) else [prev, value]
        else:
            settings[key] = value
    return settings
