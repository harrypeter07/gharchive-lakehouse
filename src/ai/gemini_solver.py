"""AI issue resolution engine using Google Gemini with Google Search Grounding.

Performs live web and GitHub retrieval to discover similar repository commits,
root cause discussions, and synthesizes actionable code patches.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Dict, Any, List


def query_gemini_with_search(api_key: str, title: str, details: str = "", model: str = "gemini-2.0-flash") -> Dict[str, Any]:
    """Query Google Gemini with real-time Google Search grounding enabled."""
    if not api_key:
        return {
            "success": False,
            "error": "No API key provided. Please enter a valid Gemini API key.",
            "text": "",
            "sources": [],
            "search_queries": [],
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = (
        f"You are a principal software engineer triaging an open-source technical issue.\n\n"
        f"Issue Title: {title}\n"
        f"Additional Context/Trace: {details if details else 'None provided'}\n\n"
        f"Search GitHub and developer documentation for real resolutions to this defect or inquiry. Then provide:\n"
        f"1. **Root Cause Analysis**: Explain why this issue happens technically.\n"
        f"2. **Recommended Code Fix / Patch**: Provide concrete code modifications or configuration diff.\n"
        f"3. **Discovered GitHub Commits / Repositories**: Cite any specific repository fixes, pull requests, or issue discussions found via search.\n"
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
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        candidates = data.get("candidates", [])
        if not candidates:
            return {
                "success": False,
                "error": "The model returned no candidate responses.",
                "text": "",
                "sources": [],
                "search_queries": [],
            }

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
        try:
            err_json = json.loads(err_body)
            msg = err_json.get("error", {}).get("message", str(err))
        except Exception:
            msg = err_body if err_body else str(err)
        return {
            "success": False,
            "error": f"API Error (HTTP {err.code}): {msg}",
            "text": "",
            "sources": [],
            "search_queries": [],
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Connection error: {exc}",
            "text": "",
            "sources": [],
            "search_queries": [],
        }
