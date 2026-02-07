# feu_tricolore/database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="simulation_feux.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.creer_table()

    def creer_table(self):
        """
        Crée la table pour stocker les statistiques de la simulation.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_num INTEGER,
                sens TEXT,
                temps_vert_moyen REAL,
                niveau_trafic_moyen REAL,
                horodatage TEXT
            )
        ''')
        self.conn.commit()

    def inserer_stats(self, cycle_num, sens, temps_vert_moyen, niveau_trafic_moyen):
        """
        Insère une ligne de statistiques dans la base de données.
        """
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute('''
            INSERT INTO stats (cycle_num, sens, temps_vert_moyen, niveau_trafic_moyen, horodatage)
            VALUES (?, ?, ?, ?, ?)
        ''', (cycle_num, sens, temps_vert_moyen, niveau_trafic_moyen, horodatage))
        self.conn.commit()

    def fermer_connexion(self):
        """
        Ferme la connexion à la base de données.
        """
        self.conn.close()
