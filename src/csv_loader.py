from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from src.config import AppConfig


def read_csv_chunks(file_path: Path, config: AppConfig) -> Iterator[pd.DataFrame]:
    expected_headers = config.expected_headers

    reader = pd.read_csv(
        file_path,
        sep=config.processing.delimiter,
        encoding=config.processing.encoding,
        chunksize=config.processing.chunksize,
        dtype=config.pandas_dtypes or None,
        keep_default_na=False,
        na_values=[""],
    )

    for chunk_number, chunk in enumerate(reader, start=1):
        actual_headers = list(chunk.columns)
        if actual_headers != expected_headers:
            raise ValueError(
                "CSV header mismatch on chunk "
                f"{chunk_number}. Expected {expected_headers}, got {actual_headers}."
            )
        yield chunk
