from datetime import datetime

from pydantic import BaseModel


class HostSnapshot(BaseModel):
    """Everything the rule engine needs about one host at one point in time."""

    host: str
    collected_at: datetime
    sources: dict[str, dict]  # source name -> normalized settings
    collection_errors: dict[str, str] = {}  # source name -> what went wrong


PARSERS = {
    "sshd_effective": "parse_sshd_effective",
    "sysctl": "parse_sysctl",
    "file_perms": "parse_stat",
    # sshd_config_raw and enabled_services get parsers as you need them
}
