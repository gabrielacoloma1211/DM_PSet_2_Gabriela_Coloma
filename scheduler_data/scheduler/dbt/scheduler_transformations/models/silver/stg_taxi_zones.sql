{{ config(materialized='view') }}

with base as (
    select * from {{ source('bronze', 'taxi_zones') }}
)

select
    locationid as zone_id,
    borough,
    zone,
    service_zone
from base