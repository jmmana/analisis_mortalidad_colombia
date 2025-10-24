import pandas as pd
from typing import Iterable

def check_row_counts(df: pd.DataFrame, min_rows: int = 1) -> None:
    if len(df) < min_rows:
        raise ValueError(f'Dataset too small: {len(df)} rows (min {min_rows})')

def check_columns(df: pd.DataFrame, expected: Iterable[str]) -> None:
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {missing}')
