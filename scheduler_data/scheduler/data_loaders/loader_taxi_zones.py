import requests
import pandas as pd
from mage_ai.data_preparation.shared.secrets import get_secret_value

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def log(msg):
    print(f"[Taxi zones] {msg}")

@data_loader
def load_data(*args, **kwargs):
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    log("Descargando taxi_zone_lookup...")

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    from io import StringIO
    df = pd.read_csv(StringIO(r.text))
    df.columns = [c.lower().strip() for c in df.columns]
    log(f"Filas={len(df)} | Columnas={list(df.columns)}")

    df["ingest_ts"] = str(pd.Timestamp.utcnow())

    log("Archivo descargado")
    return df

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
