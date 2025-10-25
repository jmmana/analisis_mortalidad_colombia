"""Simple ETL runner for development.
Usage: python etl/load_data.py --data-dir data --db-url "mysql+mysqlconnector://user:pass@host:3306/db"
"""
import argparse
import os
import pandas as pd
from sqlalchemy import create_engine

from etl.transform import normalize_columns, parse_dates, map_group_age
from etl.validators import check_row_counts, check_columns


def load_excel_to_db(path, table_name, engine):
    print(f'Reading {path}...')
    df = pd.read_excel(path, engine='openpyxl')
    print(f'Loaded {len(df)} rows, columns: {df.columns.tolist()[:5]}...')
    # Normalizar nombres de columnas
    df.columns = [col.strip().upper().replace(' ', '_') for col in df.columns]
    check_row_counts(df, min_rows=1)
    print(f'Inserting into {table_name}...')
    # naive insert for demo
    df.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=1000)
    print(f'✅ Completed: {len(df)} rows inserted into {table_name}')


def main(args):
    engine = create_engine(args.db_url)
    data_dir = args.data_dir
    files = {
        'muertes': os.path.join(data_dir, 'Anexo1.NoFetal2019_CE_15-03-23.xlsx'),
        'causas': os.path.join(data_dir, 'Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx'),
        'divipola': os.path.join(data_dir, 'Divipola_CE_.xlsx')
    }
    for table, path in files.items():
        if os.path.exists(path):
            print(f'Loading {path} -> {table}')
            load_excel_to_db(path, table, engine)
        else:
            print(f'File not found, skipping: {path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', required=True)
    parser.add_argument('--db-url', required=True)
    args = parser.parse_args()
    main(args)
