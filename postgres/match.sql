CREATE TABLE IF NOT EXISTS match
(
    match_id  BIGINT PRIMARY KEY,
    queue     SMALLINT,
    timestamp TIMESTAMP,
    duration  SMALLINT DEFAULT NULL,
    WIN       BOOLEAN  DEFAULT NULL
)