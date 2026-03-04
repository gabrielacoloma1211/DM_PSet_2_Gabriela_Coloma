import os
import time
import gc
import io
import csv

import pandas as pd
import psutil
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
from mage_ai.data_preparation.shared.secrets import get_secret_value

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


def log(msg):
    print(f"[Exporter bronze] {msg}")


def get_engine():
    host = get_secret_value("POSTGRES_HOST")
    port = get_secret_value("POSTGRES_PORT")
    db = get_secret_value("POSTGRES_DB")
    user = get_secret_value("POSTGRES_USER")
    password = get_secret_value("POSTGRES_PASSWORD")

    if not all([host, port, db, user, password]):
        raise ValueError("Faltan secretos de postgres en Mage Secrets")

    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

def ensure_schema_and_table(conn):
    #crea la tabla si no existe con metadatos minimos
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS bronze.taxi_trips (
            ingest_ts   TEXT,
            source_month TEXT,
            service_type TEXT
        );
    """))


def get_existing_cols(conn):
    rows = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema='bronze' AND table_name='taxi_trips';
    """)).fetchall()
    return {r[0] for r in rows}


def add_missing_cols(conn, existing_cols, incoming_cols):
    new_cols = sorted(incoming_cols - existing_cols)
    for c in new_cols:
        conn.execute(text(f'ALTER TABLE bronze.taxi_trips ADD COLUMN IF NOT EXISTS "{c}" TEXT;'))
        log(f"  + columna nueva: {c}")
    return existing_cols | set(new_cols)


def cast_for_copy(df: pd.DataFrame) -> pd.DataFrame:
    #solucion de error con parse
    int_cols = ["vendorid", "passenger_count", "ratecodeid", "payment_type",
                "pulocationid", "dolocationid", "trip_type"]
    for c in int_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    numeric_cols = ["trip_distance", "fare_amount", "extra", "mta_tax", "tip_amount",
                    "tolls_amount", "improvement_surcharge", "total_amount",
                    "congestion_surcharge", "airport_fee", "ehail_fee"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    ts_cols = ["tpep_pickup_datetime", "tpep_dropoff_datetime",
               "lpep_pickup_datetime", "lpep_dropoff_datetime"]
    for c in ts_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    return df


def copy_df(conn, df: pd.DataFrame):
    df = df.reindex(sorted(df.columns), axis=1)
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, quoting=csv.QUOTE_MINIMAL)
    buf.seek(0)
    cols = ",".join([f'"{c}"' for c in df.columns])
    cur = conn.connection.cursor()
    cur.copy_expert(f'COPY bronze.taxi_trips ({cols}) FROM STDIN WITH (FORMAT CSV)', buf)
    cur.close()


@data_exporter
def export_data(meta: dict, **kwargs) -> None:
    if meta["status"] != "loaded" or not meta["local_file"]:
        log("Nada que exportar.")
        return

    if not os.path.exists(meta["local_file"]):
        raise FileNotFoundError(meta["local_file"])

    service_type = meta["service_type"]
    source_month = meta["source_month"]
    ingest_ts = meta["ingest_ts"]
    local_file = meta["local_file"]

    #adapto mi batch viendo mi ram
    available_mem = psutil.virtual_memory().available
    approx_row_mem = 2000
    batch_size = min(100_000, max(50_000, int(available_mem // approx_row_mem)))
    log(f"month={source_month} service={service_type} | batch_size={batch_size}")

    parquet_file = pq.ParquetFile(local_file)
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("SET synchronous_commit = OFF;"))

        ensure_schema_and_table(conn)

        #idempotencia con el delete
        conn.execute(text("""
            DELETE FROM bronze.taxi_trips
            WHERE source_month = :sm AND service_type = :st;
        """), {"sm": source_month, "st": service_type})
        log("DELETE idempotencia OK")

        #me aseguro que exista
        parquet_cols = {c.lower() for c in parquet_file.schema_arrow.names}
        incoming_cols = parquet_cols | {"ingest_ts", "source_month", "service_type"}
        existing_cols = get_existing_cols(conn)
        existing_cols = add_missing_cols(conn, existing_cols, incoming_cols)

        total = 0
        for i, batch in enumerate(parquet_file.iter_batches(batch_size=batch_size), 1):
            df = batch.to_pandas()
            df.columns = [c.lower() for c in df.columns]
            df["ingest_ts"] = ingest_ts
            df["source_month"] = source_month
            df["service_type"] = service_type
            df = cast_for_copy(df)

            # relleno filas que estan en esta tabla
            for c in existing_cols - set(df.columns):
                df[c] = pd.NA

            copy_df(conn, df)
            total += len(df)
            if i == 1 or i % 5 == 0:
                log(f"  batch {i}: {len(df)} filas | total={total}")
            del df, batch
            gc.collect()

    log(f"DONE | total_insertado={total}")