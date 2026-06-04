# 🏠 End-to-End Data Pipeline — Marché Immobilier Marocain

> A complete data engineering pipeline for analyzing the Moroccan real estate market — from raw scraping to Power BI dashboards — built on PostgreSQL, Python, and a star-schema Data Warehouse.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Running the Pipeline](#running-the-pipeline)
- [Data Model](#data-model)
- [Power BI Dashboards](#power-bi-dashboards)
- [Logs](#logs)

---

## Overview

This project implements a full **ETL (Extract → Transform → Load)** pipeline on Moroccan real estate listings sourced from [Darkom](https://www.darkom.ma). It covers:

1. **Ingestion** of raw CSV data into a PostgreSQL staging schema
2. **Cleaning & enrichment** of listings via a Jupyter notebook
3. **Modeling** into a star-schema Data Warehouse (`bi_schema`)
4. **Visualization** through 4 Power BI dashboards

The dataset contains **1,465 cleaned listings** with fields such as price, surface area, location, property type, and publication date.

---

## Architecture

```
Raw CSV
  │
  ▼
┌─────────────────────┐
│  staging schema     │  ← load_staging.py
│  annonces_raw       │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  cleaning           │  ← cleaning.ipynb
│  (Jupyter Notebook) │
└─────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  bi_schema  (Star Schema DWH)            │  ← star_schema.py
│                                          │
│   dim_date ──┐                           │
│   dim_location ──┤── fact_annonces       │
│   dim_property ──┘                       │
└──────────────────────────────────────────┘
          │
          ▼
  Power BI (.pbix)
```

---

## Project Structure

```
.
├── data_raw/
│   └── darkom-annonces.csv          # Raw listings (1,465+ rows)
├── cleaning/
│   ├── cleaning.ipynb               # Data cleaning & feature engineering
│   └── data/
│       └── darkoum_annonces_clean.csv  # Cleaned output
├── staging/
│   └── load_staging.py              # Loads raw CSV → PostgreSQL staging schema
├── warehouse/
│   └── star_schema.py               # Builds star schema in bi_schema
├── Power_BI/
│   ├── Power_BI.pbix                # Power BI report file
│   └── Dashboards/
│       ├── Dashboard-1.png
│       ├── Dashboard-2.png
│       ├── Dashboard-3.png
│       └── Dashboard-4.png
├── logs/
│   ├── dwh_pipeline.log             # Staging pipeline logs
│   └── bi_schema.log                # Warehouse modeling logs
├── .env                             # Database credentials (not committed)
├── .gitignore
└── requirements.txt
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.x |
| Data manipulation | pandas, numpy |
| Database | PostgreSQL |
| ORM / DB connector | SQLAlchemy, psycopg2 |
| Notebook | Jupyter (ipykernel, ipython) |
| Visualization | Power BI Desktop |
| Environment | python-dotenv |
| Logging | Python `logging` module |

---

## Getting Started

### Prerequisites

- Python **3.9+**
- **PostgreSQL** running locally (default port `5432`)
- **Power BI Desktop** (to open the `.pbix` file)
- `pip` or a virtual environment manager

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/End-to-End-Data-Pipeline-immobilier-marocain.git
cd End-to-End-Data-Pipeline-immobilier-marocain

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file at the project root (or edit the existing one):

```env
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=darkom_dwh
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

Then create the database in PostgreSQL:

```sql
CREATE DATABASE darkom_dwh;
```

---

## Running the Pipeline

Execute the three stages in order:

### Step 1 — Load raw data into Staging

```bash
python staging/load_staging.py
```

This will:
- Connect to PostgreSQL
- Create the `staging` schema if it doesn't exist
- Load `data_raw/darkom-annonces.csv` into `staging.annonces_raw`
- Log the operation in `staging.logs_chargement`

### Step 2 — Clean & enrich the data

Open and run all cells in the Jupyter notebook:

```bash
jupyter notebook cleaning/cleaning.ipynb
```

The notebook will:
- Read from `staging.annonces_raw`
- Drop duplicates and handle nulls
- Extract `type_bien` from listing titles
- Engineer new features: `age_bien`, `categorie_prix`, `categorie_surface`, temporal dimensions (`annee_pub`, `mois_pub`, `trimestre_pub`)
- Export the result to `cleaning/data/darkoum_annonces_clean.csv`

### Step 3 — Build the Data Warehouse

```bash
python warehouse/star_schema.py
```

This will:
- Create the `bi_schema` schema in PostgreSQL
- Build dimension tables: `dim_date`, `dim_location`, `dim_property`
- Build the fact table: `fact_annonces`
- Load all cleaned data into the star schema
- Add indexes on foreign keys for query performance

---

## Data Model

The warehouse follows a **star schema** with one fact table and three dimension tables.

```
dim_date               dim_location           dim_property
─────────────          ────────────────       ───────────────────
date_id (PK)           location_id (PK)       property_id (PK)
date_publication       ville                  type_bien
annee_pub              quartier               transaction
mois_pub                                      nb_chambres
trimestre_pub                                 nb_salles_bain
                                              etage

                    fact_annonces
                    ─────────────────────
                    annonce_id (PK)
                    date_id (FK)
                    location_id (FK)
                    property_id (FK)
                    prix
                    surface
                    prix_m2
                    age_bien
                    categorie_prix
                    categorie_surface
```

**Price categories:**

| Category | Price range (MAD) |
|---|---|
| Économique | < 500,000 |
| Moyen | 500,000 – 1,500,000 |
| Haut standing | 1,500,000 – 3,000,000 |
| Luxe | > 3,000,000 |

**Surface categories:**

| Category | Surface (m²) |
|---|---|
| Petit | < 80 |
| Moyen | 80 – 150 |
| Grand | > 150 |

---

## Power BI Dashboards

Open `Power_BI/Power_BI.pbix` in **Power BI Desktop** and connect it to your local PostgreSQL instance (`bi_schema`).

The report includes 4 dashboards:

| Dashboard | Description |
|---|---|
| Dashboard 1 | Market overview — listings by city and type |
| Dashboard 2 | Price analysis — distributions and price per m² |
| Dashboard 3 | Temporal trends — publication trends over time |
| Dashboard 4 | Property characteristics — surface, rooms, age |

Preview screenshots are available in `Power_BI/Dashboards/`.

---

## Logs

Pipeline execution is tracked automatically:

| File | Content |
|---|---|
| `logs/dwh_pipeline.log` | Staging load operations |
| `logs/bi_schema.log` | Warehouse schema creation & data loading |

Log format: `YYYY-MM-DD HH:MM:SS - LEVEL - message`

---

## Dataset

The raw data (`darkom-annonces.csv`) contains **real estate listings** with the following columns:

`annonce_id`, `date_publication`, `titre`, `ville`, `quartier`, `type_bien`, `transaction`, `prix`, `surface`, `nb_chambres`, `nb_salles_bain`, `etage`, `annee_construction`

---

*Built as a data engineering portfolio project — Moroccan real estate market analysis.*
=======
# 🏠 End-to-End Data Pipeline — Marché Immobilier Marocain

> A complete data engineering pipeline for analyzing the Moroccan real estate market — from raw scraping to Power BI dashboards — built on PostgreSQL, Python, and a star-schema Data Warehouse.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Running the Pipeline](#running-the-pipeline)
- [Data Model](#data-model)
- [Power BI Dashboards](#power-bi-dashboards)
- [Logs](#logs)

---

## Overview

This project implements a full **ETL (Extract → Transform → Load)** pipeline on Moroccan real estate listings sourced from [Darkom](https://www.darkom.ma). It covers:

1. **Ingestion** of raw CSV data into a PostgreSQL staging schema
2. **Cleaning & enrichment** of listings via a Jupyter notebook
3. **Modeling** into a star-schema Data Warehouse (`bi_schema`)
4. **Visualization** through 4 Power BI dashboards

The dataset contains **1,465 cleaned listings** with fields such as price, surface area, location, property type, and publication date.

---

## Architecture

```
Raw CSV
  │
  ▼
┌─────────────────────┐
│  staging schema     │  ← load_staging.py
│  annonces_raw       │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  cleaning           │  ← cleaning.ipynb
│  (Jupyter Notebook) │
└─────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  bi_schema  (Star Schema DWH)            │  ← star_schema.py
│                                          │
│   dim_date ──┐                           │
│   dim_location ──┤── fact_annonces       │
│   dim_property ──┘                       │
└──────────────────────────────────────────┘
          │
          ▼
  Power BI (.pbix)
```

---

## Project Structure

```
.
├── data_raw/
│   └── darkom-annonces.csv          # Raw listings (1,465+ rows)
├── cleaning/
│   ├── cleaning.ipynb               # Data cleaning & feature engineering
│   └── data/
│       └── darkoum_annonces_clean.csv  # Cleaned output
├── staging/
│   └── load_staging.py              # Loads raw CSV → PostgreSQL staging schema
├── warehouse/
│   └── star_schema.py               # Builds star schema in bi_schema
├── Power_BI/
│   ├── Power_BI.pbix                # Power BI report file
│   └── Dashboards/
│       ├── Dashboard-1.png
│       ├── Dashboard-2.png
│       ├── Dashboard-3.png
│       └── Dashboard-4.png
├── logs/
│   ├── dwh_pipeline.log             # Staging pipeline logs
│   └── bi_schema.log                # Warehouse modeling logs
├── .env                             # Database credentials (not committed)
├── .gitignore
└── requirements.txt
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.x |
| Data manipulation | pandas, numpy |
| Database | PostgreSQL |
| ORM / DB connector | SQLAlchemy, psycopg2 |
| Notebook | Jupyter (ipykernel, ipython) |
| Visualization | Power BI Desktop |
| Environment | python-dotenv |
| Logging | Python `logging` module |

---

## Getting Started

### Prerequisites

- Python **3.9+**
- **PostgreSQL** running locally (default port `5432`)
- **Power BI Desktop** (to open the `.pbix` file)
- `pip` or a virtual environment manager

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/End-to-End-Data-Pipeline-immobilier-marocain.git
cd End-to-End-Data-Pipeline-immobilier-marocain

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file at the project root (or edit the existing one):

```env
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=darkom_dwh
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

Then create the database in PostgreSQL:

```sql
CREATE DATABASE darkom_dwh;
```

---

## Running the Pipeline

Execute the three stages in order:

### Step 1 — Load raw data into Staging

```bash
python staging/load_staging.py
```

This will:
- Connect to PostgreSQL
- Create the `staging` schema if it doesn't exist
- Load `data_raw/darkom-annonces.csv` into `staging.annonces_raw`
- Log the operation in `staging.logs_chargement`

### Step 2 — Clean & enrich the data

Open and run all cells in the Jupyter notebook:

```bash
jupyter notebook cleaning/cleaning.ipynb
```

The notebook will:
- Read from `staging.annonces_raw`
- Drop duplicates and handle nulls
- Extract `type_bien` from listing titles
- Engineer new features: `age_bien`, `categorie_prix`, `categorie_surface`, temporal dimensions (`annee_pub`, `mois_pub`, `trimestre_pub`)
- Export the result to `cleaning/data/darkoum_annonces_clean.csv`

### Step 3 — Build the Data Warehouse

```bash
python warehouse/star_schema.py
```

This will:
- Create the `bi_schema` schema in PostgreSQL
- Build dimension tables: `dim_date`, `dim_location`, `dim_property`
- Build the fact table: `fact_annonces`
- Load all cleaned data into the star schema
- Add indexes on foreign keys for query performance

---

## Data Model

The warehouse follows a **star schema** with one fact table and three dimension tables.

```
dim_date               dim_location           dim_property
─────────────          ────────────────       ───────────────────
date_id (PK)           location_id (PK)       property_id (PK)
date_publication       ville                  type_bien
annee_pub              quartier               transaction
mois_pub                                      nb_chambres
trimestre_pub                                 nb_salles_bain
                                              etage

                    fact_annonces
                    ─────────────────────
                    annonce_id (PK)
                    date_id (FK)
                    location_id (FK)
                    property_id (FK)
                    prix
                    surface
                    prix_m2
                    age_bien
                    categorie_prix
                    categorie_surface
```

**Price categories:**

| Category | Price range (MAD) |
|---|---|
| Économique | < 500,000 |
| Moyen | 500,000 – 1,500,000 |
| Haut standing | 1,500,000 – 3,000,000 |
| Luxe | > 3,000,000 |

**Surface categories:**

| Category | Surface (m²) |
|---|---|
| Petit | < 80 |
| Moyen | 80 – 150 |
| Grand | > 150 |

---

## Power BI Dashboards

Open `Power_BI/Power_BI.pbix` in **Power BI Desktop** and connect it to your local PostgreSQL instance (`bi_schema`).

The report includes 4 dashboards:

| Dashboard | Description |
|---|---|
| Dashboard 1 | Market overview — listings by city and type |
| Dashboard 2 | Price analysis — distributions and price per m² |
| Dashboard 3 | Temporal trends — publication trends over time |
| Dashboard 4 | Property characteristics — surface, rooms, age |

Preview screenshots are available in `Power_BI/Dashboards/`.

---

## Logs

Pipeline execution is tracked automatically:

| File | Content |
|---|---|
| `logs/dwh_pipeline.log` | Staging load operations |
| `logs/bi_schema.log` | Warehouse schema creation & data loading |

Log format: `YYYY-MM-DD HH:MM:SS - LEVEL - message`

---

## Dataset

The raw data (`darkom-annonces.csv`) contains **real estate listings** with the following columns:

`annonce_id`, `date_publication`, `titre`, `ville`, `quartier`, `type_bien`, `transaction`, `prix`, `surface`, `nb_chambres`, `nb_salles_bain`, `etage`, `annee_construction`

---

*Built as a data engineering portfolio project — Moroccan real estate market analysis.*
>>>>>>> c15597e (Update dashboard Power BI and documentation)
