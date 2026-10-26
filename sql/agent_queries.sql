-- =====================================================================
-- Agent Queries: Star Schema Analytical Benchmarks
-- Database: DuckDB (data/lakehouse.duckdb)
-- =====================================================================

-- Query 1: Top 10 Most Starred Repositories
-- Purpose: Identifies trending repositories on GitHub for the day by aggregating WatchEvents.
SELECT 
    r.repo_name,
    s.star_count
FROM agg_stars_per_repo_day s
JOIN dim_repo r ON s.repo_key = r.repo_key
ORDER BY s.star_count DESC
LIMIT 10;


-- Query 2: Hourly Activity Distribution by Event Type
-- Purpose: Measures peak usage hours and developer workflow patterns across the day.
SELECT 
    h.hour,
    h.event_type,
    h.event_count
FROM agg_events_per_hour h
ORDER BY h.hour ASC, h.event_count DESC;


-- Query 3: Issue Triage Ratio (Opened vs Closed Issues by Repository)
-- Purpose: Analyzes repository maintenance health by comparing new issues against resolved ones.
SELECT 
    r.repo_name,
    COUNT(CASE WHEN f.action = 'opened' THEN 1 END) AS opened_issues,
    COUNT(CASE WHEN f.action = 'closed' THEN 1 END) AS closed_issues,
    ROUND(
        COUNT(CASE WHEN f.action = 'closed' THEN 1.0 END) / 
        NULLIF(COUNT(CASE WHEN f.action = 'opened' THEN 1 END), 0), 2
    ) AS close_to_open_ratio
FROM fact_events f
JOIN dim_repo r ON f.repo_key = r.repo_key
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
WHERE det.event_type = 'IssuesEvent'
GROUP BY r.repo_name
HAVING COUNT(CASE WHEN f.action = 'opened' THEN 1 END) >= 5
ORDER BY opened_issues DESC
LIMIT 10;


-- Query 4: Window Function - Top 3 Contributing Actors Per Top Repository
-- Purpose: Uses DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...) to find primary committers.
WITH repo_actor_pushes AS (
    SELECT 
        r.repo_name,
        a.actor_key,
        COUNT(*) AS push_count
    FROM fact_events f
    JOIN dim_repo r ON f.repo_key = r.repo_key
    JOIN dim_actor a ON f.actor_key = a.actor_key
    JOIN dim_event_type det ON f.event_type_key = det.event_type_key
    WHERE det.event_type = 'PushEvent'
    GROUP BY r.repo_name, a.actor_key
),
ranked_actors AS (
    SELECT 
        repo_name,
        actor_key,
        push_count,
        DENSE_RANK() OVER (PARTITION BY repo_name ORDER BY push_count DESC) AS contributor_rank
    FROM repo_actor_pushes
)
SELECT 
    repo_name,
    contributor_rank,
    actor_key,
    push_count
FROM ranked_actors
WHERE contributor_rank <= 3
ORDER BY repo_name, contributor_rank
LIMIT 15;


-- Query 5: Unnested Issue Label Prevalence
-- Purpose: Expands list column label_names to identify the most common bug and feature categories.
SELECT 
    UNNEST(label_names) AS label_name,
    COUNT(*) AS issue_count
FROM fact_events f
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
WHERE det.event_type = 'IssuesEvent' AND f.has_labels = TRUE
GROUP BY label_name
ORDER BY issue_count DESC
LIMIT 15;
