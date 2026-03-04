{{ config(materialized='table', schema='gold') }}

select 0 as vendor_key, 'Unknown/NULL' as vendor_name
union all
select 1 as vendor_key, 'Creative Mobile Technologies, LLC' as vendor_name
union all
select 2 as vendor_key, 'VeriFone Inc.' as vendor_name
union all
select 3 as vendor_key, 'Other' as vendor_name