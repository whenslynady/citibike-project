WITH start_stations AS (
    SELECT
        station_name AS start_station_name,
        lat AS start_lat,
        lng AS start_lng
    FROM {{ ref('dim_stations') }}
),

end_stations AS (
    SELECT
        station_name AS end_station_name,
        lat AS end_lat,
        lng AS end_lng
    FROM {{ ref('dim_stations') }}
),

users AS (
    SELECT
        user_type AS member_casual
    FROM {{ ref('dim_users') }}
),

bikes AS (
    SELECT
        bike_type AS rideable_type
    FROM {{ ref('dim_bikes') }}
),

trips_with_basic_kpi AS (
    SELECT
        t.ride_id,
        t.started_at,
        t.ended_at,
        s.start_station_name,
        s.start_lat,
        s.start_lng,
        e.end_station_name,
        e.end_lat,
        e.end_lng,
        b.rideable_type,
        u.member_casual,

        -- Duration in minutes
        TIMESTAMP_DIFF(t.ended_at, t.started_at, MINUTE) AS trip_duration_minutes,

        -- Hour of day (0–23)
        EXTRACT(HOUR FROM t.started_at) AS start_hour,

        -- Trip distance in km (Haversine approximation)
    -- Trip distance in km (Haversine safe, rounded 2 decimals)
    ROUND(
        6371 * ACOS(
            LEAST(1, 
                GREATEST(-1,
                    COS(s.start_lat * 3.141592653589793 / 180)
                    * COS(e.end_lat * 3.141592653589793 / 180)
                    * COS((e.end_lng - s.start_lng) * 3.141592653589793 / 180)
                    + SIN(s.start_lat * 3.141592653589793 / 180)
                    * SIN(e.end_lat * 3.141592653589793 / 180)
                )
            )
        ), 2
    ) AS trip_distance_km


    FROM {{ ref('stg_citibike_tripdata') }} t
    LEFT JOIN start_stations s
        ON t.start_station_name = s.start_station_name
    LEFT JOIN end_stations e
        ON t.end_station_name = e.end_station_name
    LEFT JOIN users u
        ON t.member_casual = u.member_casual
    LEFT JOIN bikes b
        ON t.rideable_type = b.rideable_type
)

SELECT
    *,
    -- KPI 7: Rush hour flag (1 = 7-9am or 4-6pm)
    CASE
        WHEN start_hour BETWEEN 7 AND 9 OR start_hour BETWEEN 16 AND 18 THEN 1
        ELSE 0
    END AS is_rush_hour,

    -- KPI 8: Trip category (short/medium/long)
    CASE
        WHEN trip_duration_minutes < 10 THEN 'short'
        WHEN trip_duration_minutes BETWEEN 10 AND 30 THEN 'medium'
        ELSE 'long'
    END AS trip_category,

    -- KPI 9: Ride efficiency (distance / duration)
    ROUND(trip_distance_km / trip_duration_minutes, 3) AS ride_efficiency

FROM trips_with_basic_kpi
