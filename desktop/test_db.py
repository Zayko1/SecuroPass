# test_db.py - Pour tester la connexion à la base de données
from config import DB_CONFIG
import mysql.connector

def test_connection():
    try:
        print("Test de connexion à la base de données...")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"User: {DB_CONFIG['user']}")
        print(f"Database: {DB_CONFIG['database']}")
        
        conn = mysql.connector.connect(**DB_CONFIG)
        
        if conn.is_connected():
            print("✅ Connexion réussie!")
            
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Version MySQL: {version[0]}")
            
            # Vérifier si les tables existent
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\nTables existantes:")
            for table in tables:
                print(f"  - {table[0]}")
            
            cursor.close()
            conn.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\nVérifiez:")
        print("1. Que le serveur MySQL est accessible")
        print("2. Que les identifiants dans .env sont corrects")
        print("3. Que la base de données 'securopass' existe")

if __name__ == "__main__":
    test_connection()