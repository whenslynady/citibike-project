SELECT DISTINCT
    rideable_type AS bike_type
FROM {{ ref('stg_citibike_tripdata') }}
WHERE rideable_type IS NOT NULL
