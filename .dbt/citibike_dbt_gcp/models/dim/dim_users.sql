SELECT DISTINCT
    member_casual AS user_type
FROM {{ ref('stg_citibike_tripdata') }}
WHERE member_casual IS NOT NULL



