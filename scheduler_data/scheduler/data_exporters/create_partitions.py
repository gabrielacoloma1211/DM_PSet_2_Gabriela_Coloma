from sqlalchemy import create_engine, text
from mage_ai.data_preparation.shared.secrets import get_secret_value

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data(*args, **kwargs):
    host = get_secret_value("POSTGRES_HOST")
    port = get_secret_value("POSTGRES_PORT")
    db = get_secret_value("POSTGRES_DB")
    user = get_secret_value("POSTGRES_USER")
    password = get_secret_value("POSTGRES_PASSWORD")

    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
    
    script = """
    -- ============================================
-- PARTICIONAMIENTO DECLARATIVO PARA GOLD
-- ============================================

-- Creamos el schema analytics_gold si es que no existe ya
CREATE SCHEMA IF NOT EXISTS analytics_gold;

-- ============================================
-- 1. RANGE PARTITIONING - fct_trips
-- ============================================

DROP TABLE IF EXISTS analytics_gold.fct_trips CASCADE;

CREATE TABLE analytics_gold.fct_trips (
    trip_key                BIGSERIAL,
    pickup_date             DATE NOT NULL,
    pickup_datetime         TIMESTAMP NOT NULL,
    dropoff_datetime        TIMESTAMP NOT NULL,
    pu_zone_key             INTEGER,
    do_zone_key             INTEGER,
    service_type_key        VARCHAR(10),
    payment_type_key        INTEGER,
    vendor_key              INTEGER,
    pickup_date_key         INTEGER,
    passenger_count         INTEGER,
    trip_distance           NUMERIC(10,2),
    trip_duration_min       NUMERIC(10,2),
    fare_amount             NUMERIC(10,2),
    tip_amount              NUMERIC(10,2),
    tolls_amount            NUMERIC(10,2),
    total_amount            NUMERIC(10,2),
    source_month            VARCHAR(7),
    ingest_ts               TIMESTAMP
) PARTITION BY RANGE (pickup_date);

-- creamos las particiones del 2024
CREATE TABLE analytics_gold.fct_trips_2024_01 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE analytics_gold.fct_trips_2024_02 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE analytics_gold.fct_trips_2024_03 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
CREATE TABLE analytics_gold.fct_trips_2024_04 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
CREATE TABLE analytics_gold.fct_trips_2024_05 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');
CREATE TABLE analytics_gold.fct_trips_2024_06 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
CREATE TABLE analytics_gold.fct_trips_2024_07 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
CREATE TABLE analytics_gold.fct_trips_2024_08 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
CREATE TABLE analytics_gold.fct_trips_2024_09 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');
CREATE TABLE analytics_gold.fct_trips_2024_10 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
CREATE TABLE analytics_gold.fct_trips_2024_11 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE TABLE analytics_gold.fct_trips_2024_12 PARTITION OF analytics_gold.fct_trips FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- ============================================
-- 2. HASH PARTITIONING - dim_zone
-- ============================================

DROP TABLE IF EXISTS analytics_gold.dim_zone CASCADE;

CREATE TABLE analytics_gold.dim_zone (
    zone_key        INTEGER PRIMARY KEY,
    borough         VARCHAR(50),
    zone            VARCHAR(100),
    service_zone    VARCHAR(50)
) PARTITION BY HASH (zone_key);

-- creo las 4 particiones de hash 
CREATE TABLE analytics_gold.dim_zone_p0 PARTITION OF analytics_gold.dim_zone
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE analytics_gold.dim_zone_p1 PARTITION OF analytics_gold.dim_zone
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE analytics_gold.dim_zone_p2 PARTITION OF analytics_gold.dim_zone
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE analytics_gold.dim_zone_p3 PARTITION OF analytics_gold.dim_zone
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- ============================================
-- 3. LIST PARTITIONING - dim_service_type
-- ============================================

DROP TABLE IF EXISTS analytics_gold.dim_service_type CASCADE;

CREATE TABLE analytics_gold.dim_service_type (
    service_type_key    VARCHAR(10) PRIMARY KEY,
    service_type_name   VARCHAR(50)
) PARTITION BY LIST (service_type_key);

CREATE TABLE analytics_gold.dim_service_type_yellow PARTITION OF analytics_gold.dim_service_type
    FOR VALUES IN ('yellow');

CREATE TABLE analytics_gold.dim_service_type_green PARTITION OF analytics_gold.dim_service_type
    FOR VALUES IN ('green');

-- ============================================
-- 4. LIST PARTITIONING - dim_payment_type
-- ============================================

DROP TABLE IF EXISTS analytics_gold.dim_payment_type CASCADE;

CREATE TABLE analytics_gold.dim_payment_type (
    payment_type_key    INTEGER PRIMARY KEY,
    payment_type_name   VARCHAR(50)
) PARTITION BY LIST (payment_type_key);

CREATE TABLE analytics_gold.dim_payment_type_card PARTITION OF analytics_gold.dim_payment_type
    FOR VALUES IN (1);

CREATE TABLE analytics_gold.dim_payment_type_cash PARTITION OF analytics_gold.dim_payment_type
    FOR VALUES IN (2);

CREATE TABLE analytics_gold.dim_payment_type_other PARTITION OF analytics_gold.dim_payment_type
    FOR VALUES IN (3, 4, 5, 6);

-- ============================================
-- 5. dim_date (esta no particionamos)
-- ============================================

DROP TABLE IF EXISTS analytics_gold.dim_date CASCADE;

CREATE TABLE analytics_gold.dim_date (
    date_key            INTEGER PRIMARY KEY,
    full_date           DATE NOT NULL,
    year                INTEGER,
    month               INTEGER,
    day                 INTEGER,
    day_of_week         INTEGER,
    day_name            VARCHAR(10),
    month_name          VARCHAR(10),
    quarter             INTEGER,
    is_weekend          BOOLEAN
);

-- ============================================
-- 6. dim_vendor (igual no particionamos)
-- ============================================

DROP TABLE IF EXISTS analytics_gold.dim_vendor CASCADE;

CREATE TABLE analytics_gold.dim_vendor (
    vendor_key      INTEGER PRIMARY KEY,
    vendor_name     VARCHAR(100)
);
    """
    
    with engine.begin() as conn:
        conn.execute(text(script))
    
    print("Particiones creadas exitosamente")