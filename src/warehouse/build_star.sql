-- =====================================================================
-- Star Schema Data Warehouse DDL & Transformation Script
-- Engine: DuckDB
-- Source: Partitioned Parquet in data/clean/
-- =====================================================================

-- 1. Create Dimension: dim_date
CREATE OR REPLACE TABLE dim_date AS
WITH distinct_dates AS (
    SELECT DISTINCT CAST(event_date AS DATE) AS full_date
    FROM read_parquet('data/clean/*/*/*.parquet')
)
SELECT 
    CAST(strftime(full_date, '%Y%m%d') AS INTEGER) AS date_key,
    full_date,
    EXTRACT(year FROM full_date) AS year,
    EXTRACT(month FROM full_date) AS month,
    EXTRACT(day FROM full_date) AS day,
    strftime(full_date, '%A') AS day_of_week,
    CASE WHEN EXTRACT(dayofweek FROM full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM distinct_dates;

-- 2. Create Dimension: dim_event_type
CREATE OR REPLACE TABLE dim_event_type AS
WITH types AS (
    SELECT DISTINCT event_type
    FROM read_parquet('data/clean/*/*/*.parquet')
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY event_type) AS event_type_key,
    event_type
FROM types;

-- 3. Create Dimension: dim_repo
CREATE OR REPLACE TABLE dim_repo AS
WITH repos AS (
    SELECT 
        repo_id, 
        repo_name,
        ROW_NUMBER() OVER (PARTITION BY repo_id ORDER BY created_at DESC) AS rn
    FROM read_parquet('data/clean/*/*/*.parquet')
    WHERE repo_id IS NOT NULL
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY repo_id) AS repo_key,
    repo_id,
    repo_name,
    SPLIT_PART(repo_name, '/', 1) AS repo_owner
FROM repos
WHERE rn = 1;

-- 4. Create Dimension: dim_actor (Pseudonymised with actor_hash only)
CREATE OR REPLACE TABLE dim_actor AS
WITH actors AS (
    SELECT DISTINCT actor_hash
    FROM read_parquet('data/clean/*/*/*.parquet')
    WHERE actor_hash IS NOT NULL
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY actor_hash) AS actor_key,
    actor_hash
FROM actors;

-- 5. Create Fact Table: fact_events (Grain: One row per GitHub event)
CREATE OR REPLACE TABLE fact_events AS
SELECT 
    c.event_id,
    CAST(strftime(CAST(c.event_date AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
    det.event_type_key,
    dr.repo_key,
    da.actor_key,
    CAST(c.created_at AS TIMESTAMP) AS created_at,
    EXTRACT(hour FROM CAST(c.created_at AS TIMESTAMP)) AS hour,
    c.action,
    c.issue_number,
    c.issue_title,
    c.issue_body_first_500_chars AS issue_body,
    CASE WHEN len(c.label_names) > 0 THEN TRUE ELSE FALSE END AS has_labels,
    c.label_names,
    c.pr_merged
FROM read_parquet('data/clean/*/*/*.parquet') c
JOIN dim_event_type det ON c.event_type = det.event_type
LEFT JOIN dim_repo dr ON c.repo_id = dr.repo_id
LEFT JOIN dim_actor da ON c.actor_hash = da.actor_hash;

-- 6. Pre-computed Aggregate: agg_stars_per_repo_day
CREATE OR REPLACE TABLE agg_stars_per_repo_day AS
SELECT 
    f.date_key,
    f.repo_key,
    r.repo_name,
    COUNT(*) AS star_count
FROM fact_events f
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
JOIN dim_repo r ON f.repo_key = r.repo_key
WHERE det.event_type = 'WatchEvent' AND f.action = 'started'
GROUP BY f.date_key, f.repo_key, r.repo_name;

-- 7. Pre-computed Aggregate: agg_events_per_hour
CREATE OR REPLACE TABLE agg_events_per_hour AS
SELECT 
    f.date_key,
    f.hour,
    det.event_type,
    COUNT(*) AS event_count
FROM fact_events f
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
GROUP BY f.date_key, f.hour, det.event_type;
