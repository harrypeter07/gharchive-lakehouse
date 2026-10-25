# GLOSSARY (agent adds terms in plain words)
Format: **Term**: plain meaning. Example from this project.

- **Virtual Environment**: An isolated Python installation folder dedicated to a single project, keeping its libraries separate from the rest of your computer. Example: `.venv` created with Python 3.11 for `gharchive-lakehouse`.
- **Rate Limit**: The maximum rate of requests or tokens an API allows before temporarily blocking further calls (returning HTTP 429). Example: Google AI Studio capping Gemini Flash at 15 Requests Per Minute (RPM) and 1,500 Requests Per Day (RPD).
- **.gitignore**: A configuration file telling Git which files and directories should never be tracked or uploaded to GitHub. Example: ignoring `.env` (protecting your secret API keys) and `data/` (preventing multi-gigabyte raw files from polluting git history).
