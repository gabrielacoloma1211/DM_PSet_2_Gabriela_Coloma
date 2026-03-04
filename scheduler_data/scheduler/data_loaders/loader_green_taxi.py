import os
import time
import requests
import pandas as pd
import pyarrow.parquet as pq

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def log(msg):
    print(f"[Loader bronze] {msg}")


@data_loader
def load_data(*args, **kwargs):
    service_type = kwargs.get("service_type", "green")
    year = int(kwargs.get("year", 2024))
    month = str(kwargs.get("month", "01")).zfill(2)
    source_month = f"{year}-{month}"

    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{service_type}_tripdata_{source_month}.parquet"
    local_file = f"/tmp/{service_type}tripdata{source_month}.parquet"
    ingest_ts = pd.Timestamp.utcnow()

    log(f"service={service_type} | month={source_month} | url={url}")

    #chequeo si existe el archivo
    try:
        r = requests.head(url, allow_redirects=True, timeout=15)
        if r.status_code != 200:
            log("Archivo no encontrado (missing month)")
            return {"status": "missing", "service_type": service_type,
                    "source_month": source_month, "ingest_ts": ingest_ts,
                    "row_count": 0, "local_file": None}
    except Exception as e:
        log(f"Error verificando URL: {e}")
        return {"status": "missing", "service_type": service_type,
                "source_month": source_month, "ingest_ts": ingest_ts,
                "row_count": 0, "local_file": None}

    #me lo descargo
    if not os.path.exists(local_file):
        log("Descargando...")
        start = time.time()
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(local_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        log(f"Descarga OK en {round(time.time()-start, 1)}s | {os.path.getsize(local_file)/(1024**2):.1f} MB")
    else:
        log("Archivo ya cacheado, reutilizando")

    pf = pq.ParquetFile(local_file)
    row_count = pf.metadata.num_rows
    log(f"Filas={row_count} | Columnas={len(pf.schema_arrow.names)}")

    return {
        "status": "loaded",
        "service_type": service_type,
        "source_month": source_month,
        "ingest_ts": ingest_ts,
        "row_count": int(row_count),
        "local_file": local_file,
    }


@test
def test_output(output, *args) -> None:
    assert output is not None and isinstance(output, dict)
    assert all(k in output for k in ["status", "service_type", "source_month", "ingest_ts"])