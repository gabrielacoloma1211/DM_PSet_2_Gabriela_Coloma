import pandas as pd
from sqlalchemy import create_engine, text
from mage_ai.data_preparation.shared.secrets import get_secret_value
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

def log(msg):
    print(f"[Taxi zones] {msg}")

def get_engine():
    host = get_secret_value("POSTGRES_HOST")
    port = get_secret_value("POSTGRES_PORT")
    db   = get_secret_value("POSTGRES_DB")
    user = get_secret_value("POSTGRES_USER")
    password = get_secret_value("POSTGRES_PASSWORD")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

@data_exporter
def export_data(df: pd.DataFrame, *args, **kwargs):
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
        conn.execute(text("DROP TABLE IF EXISTS bronze.taxi_zones;"))
        df.to_sql("taxi_zones", conn, schema="bronze", if_exists="replace", index=False)
        log("Tabla bronze.taxi_zones creada...")

    log(f"{len(df)} zonas cargadas con exito")