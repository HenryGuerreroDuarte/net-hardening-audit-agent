from datetime import UTC, datetime

import paramiko

from .base import RawArtifact
from .commands import COMMANDS


class SSHCollector:
    def __init__(self, host: str, user: str, key_path: str, port: int = 22, timeout: float = 10.0):
        self.host = host
        self.user = user
        self.key_path = key_path
        self.port = port
        self.timeout = timeout

    def collect_all(self) -> list[RawArtifact]:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        client.load_system_host_keys()
        client.connect(
            self.host,
            port=self.port,
            username=self.user,
            key_filename=self.key_path,
            timeout=self.timeout,
        )
        try:
            return [self._run(client, s, c) for s, c in COMMANDS.items()]
        finally:
            client.close()

    def _run(self, client: paramiko.SSHClient, source: str, command: str) -> RawArtifact:
        _, stdout, stderr = client.exec_command(command, timeout=self.timeout)
        exit_code = stdout.channel.recv_exit_status()
        return RawArtifact(
            host=self.host,
            source=source,
            command=command,
            stdout=stdout.read().decode("utf-8", errors="replace"),
            stderr=stderr.read().decode("utf-8", errors="replace"),
            exit_code=exit_code,
            collected_at=datetime.now(UTC),
        )
