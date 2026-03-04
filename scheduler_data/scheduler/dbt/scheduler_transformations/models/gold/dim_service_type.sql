{{ config(materialized='table', schema='gold') }}

select 'yellow' as service_type_key, 'Yellow Taxi' as service_type_name
union all
select 'green' as service_type_key, 'Green Taxi' as service_type_name