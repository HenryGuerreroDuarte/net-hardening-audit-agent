from pathlib import Path

from src.parsers.sshd import parse_sshd_effective
from src.parsers.sysctl import parse_sysctl

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> str:
    return (FIXTURES / name).read_text()


def test_sshd_effective_has_expected_keys():
    settings = parse_sshd_effective(load("sshd_effective.txt"))
    # keys CIS L1 actually checks — if these parse, evaluation can work
    assert "permitrootlogin" in settings
    assert "maxauthtries" in settings


def test_sshd_repeated_keys_become_lists():
    sample = "hostkey /etc/ssh/key1\nhostkey /etc/ssh/key2\n"
    assert parse_sshd_effective(sample)["hostkey"] == ["/etc/ssh/key1", "/etc/ssh/key2"]


def test_sysctl_parses_kernel_params():
    settings = parse_sysctl(load("sysctl.txt"))
    assert "net.ipv4.ip_forward" in settings


def test_parsers_tolerate_empty_input():
    assert parse_sshd_effective("") == {}
    assert parse_sysctl("") == {}
