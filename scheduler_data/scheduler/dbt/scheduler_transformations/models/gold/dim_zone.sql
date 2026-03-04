{{ config(materialized='table', schema='gold') }}

with base as (
    select * from {{ ref('stg_taxi_zones') }}
)

select
    zone_id as zone_key,
    coalesce(borough, 'Unknown') as borough,
    coalesce(zone, 'Unknown') as zone,
    coalesce(service_zone, 'Unknown') as service_zone
from base