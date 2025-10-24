import pandas as pd
from etl.transform import normalize_columns, parse_dates


def test_normalize_and_parse():
    df = pd.DataFrame({' fecha ': ['2020-01-01'], 'edad': [30]})
    df = normalize_columns(df)
    df = parse_dates(df, col='fecha')
    assert 'fecha' in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df['fecha'])
