"""Drop reason codes for Data Quality filtering.

Each constant represents an explicit reason an event row was dropped,
ensuring zero silent drops across the pipeline.
"""

# Actor is an automated bot rather than a human developer
DROP_BOT = "BOT_ACTOR"

# Issue or Pull Request title is blank, null, or whitespace-only
DROP_EMPTY_TITLE = "EMPTY_TITLE"

# Event ID natural key has already been observed in this pipeline run
DROP_DUPLICATE_EVENT_ID = "DUPLICATE_EVENT_ID"

# IssuesEvent payload lacks the mandatory nested issue object
DROP_MISSING_PAYLOAD_ISSUE = "MISSING_PAYLOAD_ISSUE"

# created_at timestamp is malformed or not valid ISO-8601 UTC
DROP_BAD_TIMESTAMP = "BAD_TIMESTAMP"

# Event type is outside the defined scope of target lakehouse event types
DROP_UNSUPPORTED_TYPE = "UNSUPPORTED_TYPE"

# Raw line cannot be parsed as valid JSON
DROP_CORRUPT_JSON = "CORRUPT_JSON"

# Complete registry of standard drop reasons with human-readable descriptions
ALL_REASONS = {
    DROP_BOT: "Actor username ends with '[bot]'.",
    DROP_EMPTY_TITLE: "Title is missing, null, or empty whitespace.",
    DROP_DUPLICATE_EVENT_ID: "Duplicate event_id natural key encountered.",
    DROP_MISSING_PAYLOAD_ISSUE: "IssuesEvent record lacks payload.issue object.",
    DROP_BAD_TIMESTAMP: "Invalid or unparseable UTC timestamp format.",
    DROP_UNSUPPORTED_TYPE: "Event type not in target lakehouse schema scope.",
    DROP_CORRUPT_JSON: "Line failed JSON decoding syntax check.",
}
