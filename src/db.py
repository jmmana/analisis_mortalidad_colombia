import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_db_url():
    user = os.getenv('DB_USER', 'mortalidad_user')
    password = os.getenv('DB_PASS', 'mortalidad_pass')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '3306')
    db = os.getenv('DB_NAME', 'mortalidad_db')
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"

def get_engine():
    url = get_db_url()
    return create_engine(url)
