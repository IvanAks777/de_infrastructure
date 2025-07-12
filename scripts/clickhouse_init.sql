CREATE TABLE IF NOT EXISTS default.sensor_metrics (
    message_id String,
    event_time DateTime,
    sensor_id String,
    temperature Float64,
    humidity UInt32,
    pressure UInt32
) ENGINE = MergeTree()
ORDER BY (event_time, sensor_id);