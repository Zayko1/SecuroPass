import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PORT_STR = os.getenv("DB_PORT")
DB_PASS = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

missing = [var for var in ("DB_HOST","DB_USER","DB_PORT","DB_PASSWORD","DB_NAME")
           if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Variables manquantes : {', '.join(missing)}")

try:
    DB_PORT = int(DB_PORT_STR)
except ValueError:
    raise ValueError(f"DB_PORT doit être un entier, pas {DB_PORT_STR!r}")

db_config = {
    "host": DB_HOST,
    "user": DB_USER,
    "port": DB_PORT,
    "password": DB_PASS,
    "database": DB_NAME
}
