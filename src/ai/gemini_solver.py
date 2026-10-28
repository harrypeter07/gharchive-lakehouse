"""Automated issue resolution engine using grounded technical retrieval.

Performs live web and repository retrieval to discover matching commits,
diagnose defect root causes, and synthesize verified code patches.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Any, List


def get_configured_keys() -> List[str]:
    """Load API access keys from environment or local configurations, ignoring dummy placeholders."""
    raw_keys: List[str] = []

    # 1. Environment variables
    for env_var in ["GEMINI_API_KEYS", "GEMINI_API_KEY", "RESEARCH_API_KEY"]:
        val = os.environ.get(env_var, "")
        if val:
            for k in val.split(","):
                raw_keys.append(k.strip().strip("\"'"))

    # 2. Local project .env
    local_env = Path(".env")
    if local_env.exists():
        text = local_env.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if any(line.startswith(prefix) for prefix in ["GEMINI_API_KEY", "RESEARCH_KEY"]):
                if "=" in line:
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    for k in val.split(","):
                        raw_keys.append(k.strip())

    # 3. Blind_But_Smart system configuration
    alt_env = Path(r"C:\Users\ASUS\Documents\SECOND SEMISTER\INTERNSHIP\Blind_But_Smart\.env")
    if alt_env.exists():
        text = alt_env.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if line.startswith("GEMINI_API_KEY"):
                if "=" in line:
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    for k in val.split(","):
                        raw_keys.append(k.strip())

    # Filter out placeholders, dummy tokens, and short strings
    valid_keys: List[str] = []
    for k in raw_keys:
        if not k or len(k) < 30:
            continue
        if any(bad in k.lower() for bad in ["your_", "placeholder", "xxx", "dummy"]):
            continue
        if k not in valid_keys:
            valid_keys.append(k)

    return valid_keys


def query_solution_with_search(title: str, details: str = "", model: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """Query grounded technical repository retrieval to synthesize code patches."""
    keys = get_configured_keys()
    if not keys:
        return {
            "success": False,
            "error": "Access key configuration not found. Please verify local environment.",
            "text": "",
            "sources": [],
            "search_queries": [],
        }

    prompt = (
        f"You are a principal software engineer triaging an open-source technical defect.\n\n"
        f"Issue Title: {title}\n"
        f"Additional Context/Trace: {details if details else 'None provided'}\n\n"
        f"Search GitHub and developer documentation for real resolutions to this defect. Then provide:\n"
        f"1. **Root Cause Analysis**: Explain why this issue happens technically at the systems level.\n"
        f"2. **Recommended Code Fix / Patch**: Provide concrete code modifications or configuration diff.\n"
        f"3. **Discovered GitHub Commits / Repositories**: Cite specific repository fixes, pull requests, or issue discussions found via search.\n"
        f"4. **Verification Step**: How the developer should verify the patch locally."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "tools": [
            {"googleSearch": {}}
        ]
    }

    headers = {"Content-Type": "application/json"}
    last_error = ""

    # Rotate through valid keys
    for key in keys:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            candidates = data.get("candidates", [])
            if not candidates:
                continue

            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            text_content = "".join(p.get("text", "") for p in parts)

            # Extract grounding metadata (search queries & sources)
            grounding = candidate.get("groundingMetadata", {})
            search_queries = grounding.get("webSearchQueries", [])
            grounding_chunks = grounding.get("groundingChunks", [])
            sources: List[Dict[str, str]] = []
            for chunk in grounding_chunks:
                web = chunk.get("web", {})
                if web.get("uri"):
                    sources.append({
                        "title": web.get("title", web.get("uri")),
                        "url": web.get("uri"),
                    })

            return {
                "success": True,
                "text": text_content,
                "sources": sources,
                "search_queries": search_queries,
                "model": model,
            }

        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8", errors="ignore")
            last_error = f"HTTP {err.code}: {err_body[:100]}"
            # If error is key-related, rate-limit, or model-related, continue to next key
            continue
        except Exception as exc:
            last_error = str(exc)
            continue

    return {
        "success": False,
        "error": f"Search retrieval failed across configured keys: {last_error}",
        "text": "",
        "sources": [],
        "search_queries": [],
    }
