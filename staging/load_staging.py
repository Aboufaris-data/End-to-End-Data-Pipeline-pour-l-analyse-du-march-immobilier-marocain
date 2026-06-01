import pandas as pd
import os
from sqlalchemy import create_engine, text
from datetime import datetime


# Connexion PostgreSQL


USER = "postgres"
PASSWORD = "19981003"
HOST = "localhost"
PORT = "5432"
DATABASE = "darkom_dwh"

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

print("Connexion PostgreSQL réussie")


# Path CSV

current_dir = os.path.dirname(os.path.abspath(__file__)) 
project_dir = os.path.dirname(current_dir)
file_path = os.path.join(project_dir, "data_raw", "darkom-annonces.csv")

# Vérifier fichier

if not os.path.exists(file_path):
    print(f"Fichier introuvable : {file_path}")
    exit()

print("Fichier CSV trouvé")

# Lire CSV


try:
    df = pd.read_csv(file_path)

    print("CSV chargé avec succès")
    print(df.head())

except Exception as e:
    print("Erreur lecture CSV :", e)
    exit()


# Créer schema STAGING

try:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))

    print("Schema staging prêt")

except Exception as e:
    print("Erreur création schema :", e)
    exit()


# Charger données dans PostgreSQL

try:
    df.to_sql(
        name="annonces_raw",
        con=engine,
        schema="staging",
        if_exists="replace",
        index=False
    )

    print("Données insérées dans staging.annonces_raw")

except Exception as e:
    print("Erreur insertion PostgreSQL :", e)
    exit()

# Nombre lignes


nombre_lignes = len(df)

print(f"Nombre de lignes : {nombre_lignes}")

# Créer table logs


create_logs_table = """
CREATE TABLE IF NOT EXISTS staging.logs_chargement (
    id SERIAL PRIMARY KEY,
    nom_fichier VARCHAR(255),
    date_chargement TIMESTAMP,
    nombre_lignes INTEGER,
    statut VARCHAR(50)
);
"""

try:
    with engine.begin() as conn:

        conn.execute(text(create_logs_table))

        insert_log = text("""
        INSERT INTO staging.logs_chargement (
            nom_fichier,
            date_chargement,
            nombre_lignes,
            statut
        )
        VALUES (
            :nom_fichier,
            :date_chargement,
            :nombre_lignes,
            :statut
        )
        """)

        conn.execute(
            insert_log,
            {
                "nom_fichier": "darkom_annonces.csv",
                "date_chargement": datetime.now(),
                "nombre_lignes": nombre_lignes,
                "statut": "SUCCESS"
            }
        )

    print("Log ajouté avec succès")

except Exception as e:
    print("Erreur logs :", e)

# FIN

print("Pipeline STAGING terminé avec succès")