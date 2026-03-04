{{ config(materialized='view') }}

with base as (
    select * from {{ source('bronze', 'taxi_trips') }}
)

select
    service_type,
    coalesce(vendorid::int, 3) as vendor_id,
    coalesce(tpep_pickup_datetime::timestamp,lpep_pickup_datetime::timestamp) as pickup_ts,
    coalesce(tpep_dropoff_datetime::timestamp,lpep_dropoff_datetime::timestamp) as dropoff_ts,
    pulocationid::int as pickup_location_id,
    dolocationid::int as dropoff_location_id,
    passenger_count::int as passenger_count,
    trip_distance::numeric(10,2) as trip_distance,
    ratecodeid::int as rate_code_id,
    payment_type::int as payment_type,
    fare_amount::numeric(10,2) as fare_amount,
    tip_amount::numeric(10,2) as tip_amount,
    tolls_amount::numeric(10,2) as tolls_amount,
    total_amount::numeric(10,2) as total_amount,
    extract(epoch from (coalesce(tpep_dropoff_datetime::timestamp, lpep_dropoff_datetime::timestamp) - coalesce(tpep_pickup_datetime::timestamp, lpep_pickup_datetime::timestamp))) / 60.0 as trip_duration_min,
    source_month,
    ingest_ts
from base
where
    coalesce(tpep_pickup_datetime::timestamp, lpep_pickup_datetime::timestamp) is not null
    and coalesce(tpep_dropoff_datetime::timestamp, lpep_dropoff_datetime::timestamp) is not null
    and coalesce(tpep_dropoff_datetime::timestamp, lpep_dropoff_datetime::timestamp) >= coalesce(tpep_pickup_datetime::timestamp, lpep_pickup_datetime::timestamp)
    and coalesce(tpep_pickup_datetime::timestamp, lpep_pickup_datetime::timestamp) >= '2024-01-01'
    and coalesce(tpep_pickup_datetime::timestamp, lpep_pickup_datetime::timestamp) < '2026-01-01'
    and extract(epoch from (coalesce(tpep_dropoff_datetime::timestamp, lpep_dropoff_datetime::timestamp) - coalesce(tpep_pickup_datetime::timestamp, lpep_pickup_datetime::timestamp))) / 3600.0 <= 24
    and trip_distance::numeric >= 0
    and total_amount::numeric >= 0
    and passenger_count::int > 0
    and passenger_count::int <= 9