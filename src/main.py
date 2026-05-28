from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

from src.config import load_config
from src.csv_loader import read_csv_chunks
from src.sftp_client import SftpClient, SftpFile
from src.sql_client import SqlClient
from src.logger import configure_logging


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    config.processing.temp_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logging(config.processing.log_dir)

    imported_at = datetime.now()
    execution_id = imported_at.strftime("%Y%m%d_%H%M%S")
    logger.info("Starting import execution %s", execution_id)

    with SqlClient(config.sql_server) as sql_client:
        if config.processing.truncate_target_on_start:
            logger.info("Truncating target table %s", config.sql_server.target_table)
            sql_client.truncate_table(config.sql_server.target_table)

        with SftpClient(config.sftp) as sftp_client:
            files = sftp_client.list_data_files()
            logger.info("Found %s files to process", len(files))

            total_rows = 0
            failed_files = 0

            for sftp_file in files:
                rows_inserted = process_file(
                    sftp_file=sftp_file,
                    sftp_client=sftp_client,
                    sql_client=sql_client,
                    config=config,
                    execution_id=execution_id,
                    imported_at=imported_at,
                    logger=logger,
                )

                if rows_inserted is None:
                    failed_files += 1
                else:
                    total_rows += rows_inserted

    logger.info(
        "Finished import execution %s. Total rows: %s. Failed files: %s.",
        execution_id,
        total_rows,
        failed_files,
    )


def process_file(
    sftp_file: SftpFile,
    sftp_client: SftpClient,
    sql_client: SqlClient,
    config,
    execution_id: str,
    imported_at: datetime,
    logger: logging.Logger,
) -> int | None:
    started_at = datetime.now()
    rows_inserted = 0
    local_path = _local_temp_path(config.processing.temp_dir, execution_id, sftp_file)

    try:
        logger.info("Processing %s (%s bytes)", sftp_file.path, sftp_file.size_bytes)
        sftp_client.download(sftp_file.path, local_path)

        for chunk in read_csv_chunks(local_path, config):
            chunk["source_file_name"] = sftp_file.name
            chunk["source_file_path"] = sftp_file.path
            chunk["source_file_size_bytes"] = sftp_file.size_bytes
            chunk["imported_at"] = imported_at

            rows_inserted += sql_client.insert_dataframe(
                config.sql_server.target_table,
                chunk,
            )

        sql_client.commit()
        sql_client.insert_audit_record(
            audit_table=config.sql_server.audit_table,
            source_file_name=sftp_file.name,
            source_file_path=sftp_file.path,
            source_file_size_bytes=sftp_file.size_bytes,
            status="SUCCESS",
            rows_inserted=rows_inserted,
            started_at=started_at,
            finished_at=datetime.now(),
            error_message=None,
        )
        logger.info("Loaded %s rows from %s", rows_inserted, sftp_file.path)
        return rows_inserted

    except Exception as exc:
        logger.exception("Failed processing %s", sftp_file.path)
        sql_client.rollback()
        sql_client.insert_audit_record(
            audit_table=config.sql_server.audit_table,
            source_file_name=sftp_file.name,
            source_file_path=sftp_file.path,
            source_file_size_bytes=sftp_file.size_bytes,
            status="FAILED",
            rows_inserted=rows_inserted,
            started_at=started_at,
            finished_at=datetime.now(),
            error_message=str(exc)[:4000],
        )
        return None

    finally:
        if local_path.exists():
            local_path.unlink()


def _local_temp_path(temp_dir: Path, execution_id: str, sftp_file: SftpFile) -> Path:
    safe_name = sftp_file.path.replace("/", "__").replace("\\", "__")
    return temp_dir / execution_id / safe_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import SFTP CSV files into SQL Server.")
    parser.add_argument(
        "--config",
        default="config/config.local.yaml",
        help="Path to the YAML config file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
