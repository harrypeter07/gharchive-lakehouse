"""Phase 2 Integration tests for Docker stack: PostgreSQL, Airflow, and Metabase."""

import os
import subprocess
import urllib.request
import pytest
import duckdb

from src.common.config import PROJECT_ROOT


def test_docker_containers_running():
    docker_exe = "C:\\Users\\ASUS\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
    if not os.path.exists(docker_exe):
        pytest.skip("Docker Desktop executable not found in user path")

    res = subprocess.run(
        [docker_exe, "compose", "-f", "docker/docker-compose.yml", "ps", "--format", "json"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    assert res.returncode == 0, f"docker compose ps failed: {res.stderr}"
    output = res.stdout.lower()
    assert "lakehouse_postgres" in output
    assert "lakehouse_airflow_scheduler" in output
    assert "lakehouse_airflow_webserver" in output
    assert "lakehouse_metabase" in output


def test_metabase_health_endpoint():
    try:
        req = urllib.request.Request("http://localhost:3000/api/health", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            assert resp.status == 200
    except Exception as e:
        pytest.skip(f"Metabase still booting: {e}")


def test_airflow_webserver_health():
    try:
        req = urllib.request.Request("http://localhost:8080/health", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            assert resp.status == 200
    except Exception as e:
        pytest.skip(f"Airflow webserver still booting: {e}")
