{{ config(materialized='view') }}

with trips as (
    select * from {{ ref('stg_taxi_trips') }}
),

zones as (
    select * from {{ ref('stg_taxi_zones') }}
)

select
    trips.service_type,
    trips.vendor_id,
    trips.pickup_ts,
    trips.dropoff_ts,
    trips.pickup_location_id,
    trips.dropoff_location_id,
    trips.passenger_count,
    trips.trip_distance,
    trips.rate_code_id,
    trips.payment_type,
    trips.fare_amount,
    trips.tip_amount,
    trips.tolls_amount,
    trips.total_amount,
    trips.trip_duration_min,
    trips.source_month,
    trips.ingest_ts,
    pu.borough as pickup_borough,
    pu.zone as pickup_zone,
    do_.borough as dropoff_borough,
    do_.zone as dropoff_zone
from trips
left join zones as pu
    on trips.pickup_location_id = pu.zone_id
left join zones as do_
    on trips.dropoff_location_id = do_.zone_id