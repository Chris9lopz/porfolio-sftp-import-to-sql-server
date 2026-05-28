from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from stat import S_ISDIR, S_ISREG

import paramiko

from src.config import SftpConfig


@dataclass(frozen=True)
class SftpFile:
    path: str
    name: str
    size_bytes: int
    modified_at_epoch: int | None


class SftpClient:
    def __init__(self, config: SftpConfig) -> None:
        self._config = config
        self._transport: paramiko.Transport | None = None
        self._client: paramiko.SFTPClient | None = None

    def __enter__(self) -> "SftpClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def connect(self) -> None:
        transport = paramiko.Transport((self._config.host, self._config.port))
        transport.connect(
            username=self._config.username,
            password=self._config.password,
        )
        self._transport = transport
        self._client = paramiko.SFTPClient.from_transport(transport)

    def close(self) -> None:
        if self._client:
            self._client.close()
        if self._transport:
            self._transport.close()

    def list_data_files(self) -> list[SftpFile]:
        return list(
            self._walk_files(
                base_path=self._config.base_path,
                file_prefix=self._config.file_prefix,
            )
        )

    def download(self, remote_path: str, local_path: Path) -> None:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self._require_client().get(remote_path, str(local_path))

    def _walk_files(self, base_path: str, file_prefix: str):
        client = self._require_client()
        for entry in client.listdir_attr(base_path):
            entry_path = str(PurePosixPath(base_path) / entry.filename)
            mode = entry.st_mode
            if mode is not None and S_ISDIR(mode):
                yield from self._walk_files(entry_path, file_prefix)
            elif mode is not None and S_ISREG(mode) and entry.filename.startswith(file_prefix):
                yield SftpFile(
                    path=entry_path,
                    name=entry.filename,
                    size_bytes=int(entry.st_size or 0),
                    modified_at_epoch=entry.st_mtime,
                )

    def _require_client(self) -> paramiko.SFTPClient:
        if self._client is None:
            raise RuntimeError("SFTP client is not connected.")
        return self._client
