{{ config(
    materialized='view'
)}}

with source_data as (
    select
        *,
        filename as _source_filename,
        file_row_number as _source_file_row_number,
        current_timestamp as _dbt_inserted_at
    from read_parquet(
        "../data/bronze/yellow_tripdata_*.parquet",
        filename=True,
        file_row_number=True,
        union_by_name=True
    )
)

select *
from source_data