# BUGS LOG (agent: add entry for every error not fixed on first try)

## BUG-001 | status: fixed | 2026-10-25
- **Where**: `src/ingest/download_gharchive.py` / `data/raw/`
- **Symptom**: Download stalled at hour 05 (`2024-06-10-5.json.gz.tmp` 0 bytes). Error: `socket.gaierror: [Errno 11001] getaddrinfo failed` / `Resolve-DnsName : DNS operation refused (RCODE_REFUSED)`.
- **Hypotheses tried**:
  1. Wi-Fi router DNS `10.162.169.164` refused queries for `data.gharchive.org` (Result: Confirmed via `Resolve-DnsName`, `RCODE_REFUSED`).
  2. Google public DNS (`8.8.8.8`) resolves `data.gharchive.org` to `104.21.46.175` (Result: Confirmed).
  3. Python socket `getaddrinfo` fallback to Cloudflare IP preserves valid TLS SNI handshake (Result: Confirmed HTTP 200).
- **Root cause**: Host Wi-Fi DNS server (`10.162.169.164`) refused resolution of `data.gharchive.org`. Standard `urllib.request.urlopen` lacked a socket read timeout, hanging the process when DNS refused.
- **Fix**: Updated `download_gharchive.py` with DNS fallback to known edge IPs (`104.21.46.175`, `172.67.168.206`) and set `socket.setdefaulttimeout(45)`.
- **Prevention**: Explicit socket timeouts and resilient DNS fallback integrated into download pipeline.
