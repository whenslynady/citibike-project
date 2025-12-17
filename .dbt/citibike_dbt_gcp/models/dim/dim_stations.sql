WITH stations AS (
    SELECT start_station_name AS station_name,
           start_lat AS lat,
           start_lng AS lng
    FROM {{ ref('stg_citibike_tripdata') }}
    WHERE start_station_name IS NOT NULL AND start_lat IS NOT NULL AND start_lng IS NOT NULL

    UNION ALL

    SELECT end_station_name AS station_name,
           end_lat AS lat,
           end_lng AS lng
    FROM {{ ref('stg_citibike_tripdata') }}
    WHERE end_station_name IS NOT NULL AND end_lat IS NOT NULL AND end_lng IS NOT NULL
),

stations_dedup AS (
    SELECT
        station_name,
        ANY_VALUE(lat) AS lat,
        ANY_VALUE(lng) AS lng
    FROM stations
    GROUP BY station_name
)

SELECT *
FROM stations_dedup
