# DECISIONS (agent: add entry per choice)
Template: ## D-001 | date | topic
- Chosen:  - Why:  - Alternatives rejected:  - Revisit if:

## D-001 | 2026-10-25 | Gemini Free-Tier Limits and Model Selection
- **Chosen**: `gemini-1.5-flash` / `gemini-2.0-flash` for any optional LLM silver-labeling or SQL helper tasks.
- **Current Official Limits (verified from https://ai.google.dev/gemini-api/docs/rate-limits and https://ai.google.dev/gemini-api/docs/models)**:
  - RPM (Requests Per Minute): 15 RPM
  - TPM (Tokens Per Minute): 1,000,000 TPM
  - RPD (Requests Per Day): 1,500 RPD
  - Quota reset: Daily at midnight Pacific Time (PT)
- **Why**: Fastest response times, highest daily quota (1,500 RPD vs 50 RPD for Pro), and completely free without credit card.
- **Alternatives rejected**: `gemini-1.5-pro` (capped at 2 RPM / 50 RPD in free tier, too small for batch work); paid APIs.
- **Revisit if**: Google modifies free-tier quotas or model deprecation notices are posted on ai.google.dev.
