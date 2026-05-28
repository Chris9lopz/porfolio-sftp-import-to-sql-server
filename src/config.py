from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ColumnConfig:
    name: str
    sql_type: str
    pandas_dtype: str | None = None
    nullable: bool = True


@dataclass(frozen=True)
class SftpConfig:
    host: str
    port: int
    username: str
    password: str
    base_path: str
    file_prefix: str


@dataclass(frozen=True)
class SqlServerConfig:
    driver: str
    server: str
    database: str
    trusted_connection: bool
    username: str
    password: str
    target_table: str
    audit_table: str


@dataclass(frozen=True)
class ProcessingConfig:
    delimiter: str
    encoding: str
    chunksize: int
    temp_dir: Path
    log_dir: Path
    truncate_target_on_start: bool


@dataclass(frozen=True)
class AppConfig:
    sftp: SftpConfig
    sql_server: SqlServerConfig
    processing: ProcessingConfig
    columns: list[ColumnConfig]

    @property
    def expected_headers(self) -> list[str]:
        return [column.name for column in self.columns]

    @property
    def pandas_dtypes(self) -> dict[str, str]:
        return {
            column.name: column.pandas_dtype
            for column in self.columns
            if column.pandas_dtype
        }


def load_config(config_path: str | Path) -> AppConfig:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as config_file:
        raw = yaml.safe_load(config_file)

    return _parse_config(raw, path.parent)


def _parse_config(raw: dict[str, Any], config_dir: Path) -> AppConfig:
    sftp = raw["sftp"]
    sql = raw["sql_server"]
    processing = raw["processing"]
    schema = raw["schema"]

    temp_dir = _resolve_path(processing["temp_dir"], config_dir)
    log_dir = _resolve_path(processing["log_dir"], config_dir)

    return AppConfig(
        sftp=SftpConfig(
            host=sftp["host"],
            port=int(sftp.get("port", 22)),
            username=sftp["username"],
            password=sftp["password"],
            base_path=sftp["base_path"],
            file_prefix=sftp.get("file_prefix", "data_"),
        ),
        sql_server=SqlServerConfig(
            driver=sql["driver"],
            server=sql["server"],
            database=sql["database"],
            trusted_connection=bool(sql.get("trusted_connection", True)),
            username=sql.get("username", ""),
            password=sql.get("password", ""),
            target_table=sql["target_table"],
            audit_table=sql["audit_table"],
        ),
        processing=ProcessingConfig(
            delimiter=processing.get("delimiter", ","),
            encoding=processing.get("encoding", "utf-8"),
            chunksize=int(processing.get("chunksize", 50000)),
            temp_dir=temp_dir,
            log_dir=log_dir,
            truncate_target_on_start=bool(
                processing.get("truncate_target_on_start", True)
            ),
        ),
        columns=[
            ColumnConfig(
                name=column["name"],
                sql_type=column["sql_type"],
                pandas_dtype=column.get("pandas_dtype"),
                nullable=bool(column.get("nullable", True)),
            )
            for column in schema["columns"]
        ],
    )


def _resolve_path(value: str, config_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (config_dir.parent / path).resolve()
