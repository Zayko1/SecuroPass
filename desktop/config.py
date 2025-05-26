import os
from dotenv import load_dotenv

# 1. Charge le .env à la racine du projet (ou les vars système)
load_dotenv()

# 2. Récupère et valide chaque variable
DB_HOST     = os.getenv("DB_HOST")
DB_USER     = os.getenv("DB_USER")
DB_PORT_STR = os.getenv("DB_PORT")
DB_PASS     = os.getenv("DB_PASSWORD")
DB_NAME     = os.getenv("DB_NAME")

# 3. Assurez-vous que rien n'est manquant
missing = [var for var in ("DB_HOST","DB_USER","DB_PORT","DB_PASSWORD","DB_NAME")
           if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Variables manquantes : {', '.join(missing)}")

# 4. Convertit le port en int (ou lève une erreur)
try:
    DB_PORT = int(DB_PORT_STR)
except ValueError:
    raise ValueError(f"DB_PORT doit être un entier, pas {DB_PORT_STR!r}")

# 5. Construit enfin la config
db_config = {
    "host":     DB_HOST,
    "user":     DB_USER,
    "port":     DB_PORT,
    "password": DB_PASS,
    "database": DB_NAME
}
