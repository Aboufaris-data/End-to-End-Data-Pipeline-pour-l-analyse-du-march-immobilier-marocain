import os
import logging
import pandas as pd

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# =========================
# LOGGING
# =========================

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/bi_schema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Starting Data Warehouse Modeling")

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# =========================
# DATABASE CONNECTION
# =========================

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

logging.info("Database connected")

# =========================
# LOAD CLEAN DATA
# =========================

df = pd.read_csv(r"cleaning/data/darkoum_annonces_clean.csv")

df["date_publication"] = pd.to_datetime(
    df["date_publication"],
    errors="coerce"
)
df["annee_pub"] = df["date_publication"].dt.year
df["mois_pub"] = df["date_publication"].dt.month
df["trimestre_pub"] = df["date_publication"].dt.quarter

# CREATE BI SCHEMA

with engine.begin() as conn:

    conn.execute(text("""

    CREATE SCHEMA IF NOT EXISTS bi_schema;

    DROP TABLE IF EXISTS bi_schema.fact_annonces CASCADE;
    DROP TABLE IF EXISTS bi_schema.dim_date CASCADE;
    DROP TABLE IF EXISTS bi_schema.dim_location CASCADE;
    DROP TABLE IF EXISTS bi_schema.dim_property CASCADE;

    -- =====================
    -- DIM DATE
    -- =====================

    CREATE TABLE bi_schema.dim_date (
        date_id SERIAL PRIMARY KEY,
        date_publication DATE UNIQUE,
        annee_pub INT,
        mois_pub INT,
        trimestre_pub INT
    );

    -- =====================
    -- DIM LOCATION
    -- =====================

    CREATE TABLE bi_schema.dim_location (
        location_id SERIAL PRIMARY KEY,
        ville VARCHAR(255),
        quartier VARCHAR(255)
    );

    -- =====================
    -- DIM PROPERTY
    -- =====================

    CREATE TABLE bi_schema.dim_property (
        property_id SERIAL PRIMARY KEY,
        type_bien VARCHAR(100),
        transaction VARCHAR(100),
        nb_chambres INT,
        nb_salles_bain INT,
        etage INT
    );

    -- =====================
    -- FACT TABLE
    -- =====================

    CREATE TABLE bi_schema.fact_annonces (

        annonce_id SERIAL PRIMARY KEY,

        date_id INT,
        location_id INT,
        property_id INT,

        prix BIGINT,
        surface INT,
        prix_m2 FLOAT,
        age_bien INT,

        categorie_prix VARCHAR(100),
        categorie_surface VARCHAR(100),

        FOREIGN KEY (date_id)
        REFERENCES bi_schema.dim_date(date_id),

        FOREIGN KEY (location_id)
        REFERENCES bi_schema.dim_location(location_id),

        FOREIGN KEY (property_id)
        REFERENCES bi_schema.dim_property(property_id)
    );

    """))

logging.info("Star schema created")


# DIMENSIONS

df_dim_date = df[[
    "date_publication",
    "annee_pub",
    "mois_pub",
    "trimestre_pub"
]].drop_duplicates()

df_dim_location = df[[
    "ville",
    "quartier"
]].drop_duplicates()

df_dim_property = df[[
    "type_bien",
    "transaction",
    "nb_chambres",
    "nb_salles_bain",
    "etage"
]].drop_duplicates()


# LOAD DIMENSIONS
df_dim_date.to_sql(
    "dim_date",
    engine,
    schema="bi_schema",
    if_exists="append",
    index=False
)

df_dim_location.to_sql(
    "dim_location",
    engine,
    schema="bi_schema",
    if_exists="append",
    index=False
)

df_dim_property.to_sql(
    "dim_property",
    engine,
    schema="bi_schema",
    if_exists="append",
    index=False
)

logging.info("Dimensions loaded")


# RELOAD DIMENSIONS


df_dim_date = pd.read_sql(
    "SELECT * FROM bi_schema.dim_date",
    engine
)

df_dim_date["date_publication"] = pd.to_datetime(
    df_dim_date["date_publication"]
    
)
df_dim_location = pd.read_sql(
    "SELECT * FROM bi_schema.dim_location",
    engine
)

df_dim_property = pd.read_sql(
    "SELECT * FROM bi_schema.dim_property",
    engine
)

df["prix_m2"] = df["prix"] / df["surface"]

# MERGE FOREIGN KEYS


df = df.merge(
    df_dim_date,
    on="date_publication",
    how="left"
)

df = df.merge(
    df_dim_location,
    on=["ville", "quartier"],
    how="left"
)

df = df.merge(
    df_dim_property,
    on=[
        "type_bien",
        "transaction",
        "nb_chambres",
        "nb_salles_bain",
        "etage"
    ],
    how="left"
)

logging.info("Foreign keys merged")

# FACT TABLE


df_fact = df[[
    "date_id",
    "location_id",
    "property_id",
    "prix",
    "surface",
    "prix_m2",
    "age_bien",
    "categorie_prix",
    "categorie_surface"
]]


# LOAD FACT TABLE


df_fact.to_sql(
    "fact_annonces",
    engine,
    schema="bi_schema",
    if_exists="append",
    index=False,
    method="multi",
    chunksize=500
)

logging.info(f"Fact table loaded: {len(df_fact)} rows")


# INDEXATION


with engine.begin() as conn:

    conn.execute(text("""

    CREATE INDEX IF NOT EXISTS idx_fact_date
    ON bi_schema.fact_annonces(date_id);

    CREATE INDEX IF NOT EXISTS idx_fact_location
    ON bi_schema.fact_annonces(location_id);

    CREATE INDEX IF NOT EXISTS idx_fact_property
    ON bi_schema.fact_annonces(property_id);

    """))

logging.info("Indexes created")


# DATA QUALITY CHECK

null_check = df_fact.isnull().sum()

print(null_check)

logging.info("Data quality check completed")

# END

print("Data Warehouse Modeling completed successfully")

logging.info("Pipeline completed")