-- =====================================================================
-- Guided SQL Analytics: Star Schema Queries & Explanations
-- Target Tables: fact_events, dim_repo, dim_actor, dim_event_type, dim_date
-- Engine: DuckDB (data/lakehouse.duckdb)
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Top 10 Repositories by Stars Gained
-- ---------------------------------------------------------------------
-- BUSINESS QUESTION: Which GitHub repositories were trending and gained the
-- most stars on this date?
-- WHY WE WROTE THIS: In an analytics team, leadership wants to see trending
-- projects. In GitHub data, giving a star corresponds to a 'WatchEvent' with action='started'.
-- HOW IT WORKS:
-- 1. We join fact_events to dim_repo using the surrogate foreign key repo_key.
-- 2. We join dim_event_type to filter only 'WatchEvent'.
-- 3. We group by repo_name, count the stars, and sort descending.
SELECT 
    r.repo_name,
    COUNT(*) AS total_stars
FROM fact_events f
JOIN dim_repo r ON f.repo_key = r.repo_key
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
WHERE det.event_type = 'WatchEvent' 
  AND f.action = 'started'
GROUP BY r.repo_name
ORDER BY total_stars DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- QUERY 2: Hourly Distribution of Events Across the Day
-- ---------------------------------------------------------------------
-- BUSINESS QUESTION: At what hours of the day does global GitHub traffic peak?
-- WHY WE WROTE THIS: Infrastructure engineers need traffic curves to plan compute
-- capacity and scale cloud clusters up or down.
-- HOW IT WORKS:
-- 1. We extract the 'hour' column (0 to 23) from fact_events.
-- 2. We use conditional aggregation (CASE WHEN) to count pushes, PRs, and stars separately.
-- 3. Grouping by hour creates a chronological 24-hour timeline.
SELECT 
    f.hour,
    COUNT(*) AS total_events,
    COUNT(CASE WHEN det.event_type = 'PushEvent' THEN 1 END) AS code_pushes,
    COUNT(CASE WHEN det.event_type = 'PullRequestEvent' THEN 1 END) AS pull_requests,
    COUNT(CASE WHEN det.event_type = 'WatchEvent' THEN 1 END) AS stars
FROM fact_events f
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
GROUP BY f.hour
ORDER BY f.hour ASC;


-- ---------------------------------------------------------------------
-- QUERY 3: Repository Issue Resolution Ratio (Opened vs Closed)
-- ---------------------------------------------------------------------
-- BUSINESS QUESTION: Which repositories are responsive to bug reports and feature
-- requests versus which repositories have a growing backlog?
-- WHY WE WROTE THIS: Measures open-source project maintenance health.
-- HOW IT WORKS:
-- 1. We filter fact_events for 'IssuesEvent'.
-- 2. We count how many times action was 'opened' vs 'closed'.
-- 3. We use NULLIF() to prevent division-by-zero errors if opened is 0.
-- 4. HAVING ensures we only analyze repositories with at least 10 issues opened.
SELECT 
    r.repo_name,
    COUNT(CASE WHEN f.action = 'opened' THEN 1 END) AS opened_count,
    COUNT(CASE WHEN f.action = 'closed' THEN 1 END) AS closed_count,
    ROUND(
        COUNT(CASE WHEN f.action = 'closed' THEN 1.0 END) / 
        NULLIF(COUNT(CASE WHEN f.action = 'opened' THEN 1 END), 0), 2
    ) AS closed_to_opened_ratio
FROM fact_events f
JOIN dim_repo r ON f.repo_key = r.repo_key
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
WHERE det.event_type = 'IssuesEvent'
GROUP BY r.repo_name
HAVING COUNT(CASE WHEN f.action = 'opened' THEN 1 END) >= 10
ORDER BY opened_count DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- QUERY 4: Window Function - Top 3 Repositories Within Each Event Type
-- ---------------------------------------------------------------------
-- BUSINESS QUESTION: Who are the top 3 repositories for code pushes, top 3 for
-- pull requests, and top 3 for stars?
-- WHY WE WROTE THIS: In interviews, window functions (PARTITION BY ... ORDER BY ...)
-- are heavily tested. A simple GROUP BY only gives global top repos, whereas window functions
-- rank records *within independent sub-groups*.
-- HOW IT WORKS:
-- 1. CTE (Common Table Expression) 'repo_event_counts' groups by event_type and repo.
-- 2. DENSE_RANK() OVER (PARTITION BY event_type ORDER BY event_count DESC) ranks
--    repositories 1, 2, 3... restarting the rank count for every event type.
-- 3. The outer query filters for rank <= 3.
WITH repo_event_counts AS (
    SELECT 
        det.event_type,
        r.repo_name,
        COUNT(*) AS event_count
    FROM fact_events f
    JOIN dim_event_type det ON f.event_type_key = det.event_type_key
    JOIN dim_repo r ON f.repo_key = r.repo_key
    GROUP BY det.event_type, r.repo_name
),
ranked_repos AS (
    SELECT 
        event_type,
        repo_name,
        event_count,
        DENSE_RANK() OVER (
            PARTITION BY event_type 
            ORDER BY event_count DESC
        ) AS rank_in_type
    FROM repo_event_counts
)
SELECT 
    event_type,
    rank_in_type,
    repo_name,
    event_count
FROM ranked_repos
WHERE rank_in_type <= 3
ORDER BY event_type, rank_in_type;


-- ---------------------------------------------------------------------
-- QUERY 5: Prolific Developers (Top Actors by Code Pushes)
-- ---------------------------------------------------------------------
-- BUSINESS QUESTION: Who are the most active human developers committing code,
-- and does our privacy pseudonymisation protect their personal identity?
-- WHY WE WROTE THIS: Proves that our privacy layer works. In dim_actor, we only
-- store a 64-character SHA-256 hash (never raw usernames).
-- HOW IT WORKS:
-- 1. We join fact_events with dim_actor using actor_key.
-- 2. We filter for 'PushEvent'.
-- 3. We group by actor_key and display the secure actor_hash with their push volume.
SELECT 
    a.actor_key,
    SUBSTR(a.actor_hash, 1, 16) || '...' AS masked_actor_hash,
    COUNT(*) AS push_event_count,
    COUNT(DISTINCT f.repo_key) AS distinct_repos_contributed
FROM fact_events f
JOIN dim_actor a ON f.actor_key = a.actor_key
JOIN dim_event_type det ON f.event_type_key = det.event_type_key
WHERE det.event_type = 'PushEvent'
GROUP BY a.actor_key, a.actor_hash
ORDER BY push_event_count DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- QUERY 6: Window Function - Cumulative Running Total of Events Across the Day
-- ---------------------------------------------------------------------
-- BUSINESS QUESTION: How does event volume build up hour-by-hour to reach the
-- 2 million event mark at the end of the day?
-- WHY WE WROTE THIS: Running totals (cumulative aggregations) are used in business
-- to track daily revenue pacing, ride-hailing completed trips, or pipeline throughput.
-- HOW IT WORKS:
-- 1. Inner query computes total events for each hour.
-- 2. SUM(hourly_events) OVER (ORDER BY hour ASC ROWS BETWEEN UNBOUNDED PRECEDING
--    AND CURRENT ROW) adds the current hour's events to all previous hours.
WITH hourly_totals AS (
    SELECT 
        hour,
        COUNT(*) AS hourly_events
    FROM fact_events
    GROUP BY hour
)
SELECT 
    hour,
    hourly_events,
    SUM(hourly_events) OVER (
        ORDER BY hour ASC 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_cumulative_events
FROM hourly_totals
ORDER BY hour ASC;
