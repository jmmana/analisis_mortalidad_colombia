import pandas as pd

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: c.strip())
    return df

def parse_dates(df: pd.DataFrame, col: str = 'fecha') -> pd.DataFrame:
    df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def map_group_age(df: pd.DataFrame, col: str = 'GRUPO_EDAD1') -> pd.DataFrame:
    # example mapping, adapt to real dataset
    mapping = {
        0: '0-1',
        1: '1-9',
        2: '10-19',
        3: '20-29'
    }
    if col in df.columns:
        df['grupo_edad'] = df[col].map(mapping).fillna('desconocido')
    return df
