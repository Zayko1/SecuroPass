import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "217.154.24.244"),
    "user": os.getenv("DB_USER", "root"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "password": os.getenv("DB_PASSWORD", "IndienTéméraire19%"),
    "database": os.getenv("DB_NAME", "securopass")
}