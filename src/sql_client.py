from __future__ import annotations

from datetime import datetime

import pandas as pd
import pyodbc

from src.config import SqlServerConfig


class SqlClient:
    def __init__(self, config: SqlServerConfig) -> None:
        self._config = config
        self._connection: pyodbc.Connection | None = None

    def __enter__(self) -> "SqlClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def connect(self) -> None:
        self._connection = pyodbc.connect(self._connection_string())
        self._connection.autocommit = False

    def close(self) -> None:
        if self._connection:
            self._connection.close()

    def truncate_table(self, table_name: str) -> None:
        connection = self._require_connection()
        cursor = connection.cursor()
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        connection.commit()

    def commit(self) -> None:
        self._require_connection().commit()

    def rollback(self) -> None:
        self._require_connection().rollback()

    def insert_dataframe(self, table_name: str, dataframe: pd.DataFrame) -> int:
        if dataframe.empty:
            return 0

        connection = self._require_connection()
        cursor = connection.cursor()
        cursor.fast_executemany = True

        columns = list(dataframe.columns)
        placeholders = ", ".join(["?"] * len(columns))
        column_sql = ", ".join(f"[{column}]" for column in columns)
        insert_sql = f"INSERT INTO {table_name} ({column_sql}) VALUES ({placeholders})"

        rows = [tuple(_normalize_value(value) for value in row) for row in dataframe.itertuples(index=False, name=None)]
        cursor.executemany(insert_sql, rows)
        return len(rows)

    def insert_audit_record(
        self,
        audit_table: str,
        source_file_name: str,
        source_file_path: str,
        source_file_size_bytes: int | None,
        status: str,
        rows_inserted: int | None,
        started_at: datetime,
        finished_at: datetime | None,
        error_message: str | None,
    ) -> None:
        connection = self._require_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO {audit_table} (
                source_file_name,
                source_file_path,
                source_file_size_bytes,
                status,
                rows_inserted,
                started_at,
                finished_at,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            source_file_name,
            source_file_path,
            source_file_size_bytes,
            status,
            rows_inserted,
            started_at,
            finished_at,
            error_message,
        )
        connection.commit()

    def _connection_string(self) -> str:
        parts = [
            f"DRIVER={{{self._config.driver}}}",
            f"SERVER={self._config.server}",
            f"DATABASE={self._config.database}",
        ]

        if self._config.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            parts.extend(
                [
                    f"UID={self._config.username}",
                    f"PWD={self._config.password}",
                ]
            )

        return ";".join(parts)

    def _require_connection(self) -> pyodbc.Connection:
        if self._connection is None:
            raise RuntimeError("SQL Server connection is not open.")
        return self._connection


def _normalize_value(value):
    if pd.isna(value):
        return None
    return value
