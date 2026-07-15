def parse_sysctl(text: str) -> dict[str, str]:
    """Parse `sysctl -a` output: 'key = value' per line."""
    settings = {}
    for line in text.splitlines():
        if "=" not in line:
            continue  # skips permission-error noise and blank lines
        key, _, value = line.partition("=")
        settings[key.strip()] = value.strip()
    return settings
