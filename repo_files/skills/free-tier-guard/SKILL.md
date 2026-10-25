# SKILL: free-tier-guard (keep everything free and safe)
Allowed (free): Python libs, DuckDB, PySpark, PyTorch, Streamlit, Docker Desktop (personal/education use; check current license terms), Postgres, Airflow, Kafka, Metabase OSS, GH Archive, Colab free tier, Gemini API free tier, BigQuery sandbox (no card).
Ask first if: any signup, credit card prompt, "trial", billing setup, paid model/API, or unclear license.

## Gemini API
- Key only in `.env` as GEMINI_API_KEY, loaded with python-dotenv. Never print it.
- Before use, fetch CURRENT free-tier limits and model names from https://ai.google.dev/gemini-api/docs/rate-limits and https://ai.google.dev/gemini-api/docs/models. Do not trust memory.
- Always: batch several items per request, cache every response on disk (`data/cache/`), back off on 429, cap total calls (configurable), log call count.
- Free-tier inputs may be used by Google to improve products: send only public GH Archive text, nothing personal.
- Use Gemini only for: silver labels (Plan B), optional text-to-SQL tab (SELECT only, read-only connection), optional explanations. The core pipeline must work without it.

## Colab
Sessions disconnect and RAM is limited: keep to one day of data, re-run from the repo, save outputs to Drive.

## BigQuery sandbox
Show estimated bytes scanned before each query; select few columns; stay far below the free quota.

## Tunnels for Streamlit in Colab
Try cloudflared quick tunnel first (no account). ngrok needs a free account + auth token: guide step by step; token goes in Colab Secrets, never in the notebook.
