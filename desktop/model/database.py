#model > database.py
import mysql.connector
from mysql.connector import Error


def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='app',
        password='dev',
        database='securopass'
    )

def test_connection():
    try:
        connection = get_connection()

        if connection.is_connected():
            print("✅ Connexion réussie à la base de données !")
            db_info = connection.get_server_info()
            print("Version du serveur MySQL :", db_info)

    except Error as e:
        print("❌ Erreur de connexion :", e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔒 Connexion fermée.")
            
test_connection()   