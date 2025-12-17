SELECT
  ride_id,
  TIMESTAMP_MILLIS(CAST(started_at / 1000000 AS INT64)) AS started_at,
  TIMESTAMP_MILLIS(CAST(ended_at / 1000000 AS INT64)) AS ended_at,
  COALESCE(start_station_name, 'Unknown') AS start_station_name,
  COALESCE(end_station_name, 'Unknown') AS end_station_name,
  rideable_type,
  member_casual,
  start_lat,
  start_lng,
  end_lat,
  end_lng
FROM {{ source('citibike_source', 'citibike_tripdata_partitioned_2025') }}
