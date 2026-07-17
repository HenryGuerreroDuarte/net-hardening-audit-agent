# source name -> command. Read-only commands only — this is the project's
# core safety property, so keep every command here auditable at a glance.
COMMANDS: dict[str, str] = {
    "sshd_effective": "sudo -n sshd -T",
    "sshd_config_raw": "cat /etc/ssh/sshd_config",
    "sysctl": "sysctl -a 2>/dev/null",
    "enabled_services": "systemctl list-unit-files --type=service --state=enabled --no-legend",
    "file_perms": (
        "stat -c '%n %a %U %G' /etc/passwd /etc/shadow /etc/group /etc/gshadow /etc/ssh/sshd_config"
    ),
}
