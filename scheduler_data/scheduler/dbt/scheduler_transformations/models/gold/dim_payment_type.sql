{{ config(materialized='table', schema='gold') }}

select 1 as payment_type_key, 'Credit Card' as payment_type_name
union all
select 2 as payment_type_key, 'Cash' as payment_type_name
union all
select 3 as payment_type_key, 'No Charge' as payment_type_name
union all
select 4 as payment_type_key, 'Dispute' as payment_type_name
union all
select 5 as payment_type_key, 'Unknown' as payment_type_name
union all
select 6 as payment_type_key, 'Voided Trip' as payment_type_name