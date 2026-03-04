{{ config(materialized='table', schema='gold') }}

with enriched_trips as (
    select * from {{ ref('int_trips_enriched') }}
)

select
    row_number() over ()::bigint as trip_key,
    pickup_ts::date as pickup_date,
    pickup_ts as pickup_datetime,
    dropoff_ts as dropoff_datetime,
    pickup_location_id as pu_zone_key,
    dropoff_location_id as do_zone_key,
    service_type as service_type_key,
    payment_type as payment_type_key,
    coalesce(vendor_id, 0) as vendor_key,
    to_char(pickup_ts, 'YYYYMMDD')::integer as pickup_date_key,
    passenger_count,
    trip_distance,
    trip_duration_min,
    fare_amount,
    tip_amount,
    tolls_amount,
    total_amount,
    source_month,
    ingest_ts
from enriched_trips
where pickup_ts::date >= '2024-01-01'
and pickup_ts::date < '2025-01-01'