{{ config(materialized='table', schema='gold') }}

with date_spine as (
    select
        generate_series(
            '2024-01-01'::date,
            '2024-12-31'::date,
            '1 day'::interval
        )::date as full_date
)

select
    to_char(full_date, 'YYYYMMDD')::integer as date_key,
    full_date,
    extract(year from full_date)::integer as year,
    extract(month from full_date)::integer as month,
    extract(day from full_date)::integer as day,
    extract(dow from full_date)::integer as day_of_week,
    to_char(full_date, 'Day') as day_name,
    to_char(full_date, 'Month') as month_name,
    extract(quarter from full_date)::integer as quarter,
    extract(dow from full_date) in (0, 6) as is_weekend
from date_spine