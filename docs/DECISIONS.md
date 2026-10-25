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

## D-002 | 2026-10-25 | Issue Classification Ground Truth: Plan A (GitHub Natural Labels)
- **Chosen**: Plan A (use GitHub's natural labels as ground truth for IR and ML classification).
- **Why**: Inspection of `2024-06-10-15.json.gz` revealed 1,953 labeled IssuesEvent rows (44.58% label rate). Specifically, bug/enhancement/feature/question labels accounted for ~900 rows in a single hour (~20.5% of all issues, far above the 1.5% threshold). A full 24-hour day will produce an estimated 21,600+ labeled issues, comfortably exceeding the 3,000 threshold required for robust training without needing artificial silver labels.
- **Alternatives rejected**: Plan B (LLM-based silver labeling via Gemini API). Plan B is kept as an optional auxiliary validation or text-to-SQL enhancement rather than the primary ground truth.
- **Revisit if**: Full-day download reveals unexpected sparsity in specific classes or a severe label distribution shift across off-peak hours.
