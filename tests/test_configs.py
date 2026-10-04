"""Test: i dataset.yml sono validi (preflight toolkit)."""

import glob
import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
DATASET_CONFIGS = sorted(glob.glob(os.path.join(REPO_ROOT, "datasets", "*", "dataset.yml")))
COMPOSE_CONFIGS = sorted(glob.glob(os.path.join(REPO_ROOT, "compose", "*", "dataset.yml")))


@pytest.mark.policy
@pytest.mark.parametrize(
    "config_path",
    DATASET_CONFIGS,
    ids=[os.path.basename(os.path.dirname(p)) for p in DATASET_CONFIGS],
)
def test_dataset_preflight(config_path):
    """Ogni dataset.yml deve passare il preflight del toolkit."""
    result = subprocess.run(
        ["toolkit", "run", "preflight", "--config", config_path],
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "TOOLKIT_ALLOW_SCRIPT_SOURCE": "1"},
        check=False,
    )
    assert result.returncode == 0, f"Preflight fallito per {config_path}:\n{result.stderr[-500:]}"


@pytest.mark.policy
@pytest.mark.parametrize(
    "config_path",
    COMPOSE_CONFIGS,
    ids=[os.path.basename(os.path.dirname(p)) for p in COMPOSE_CONFIGS],
)
def test_compose_preflight(config_path):
    """Ogni compose dataset.yml deve passare il preflight."""
    result = subprocess.run(
        ["toolkit", "run", "preflight", "--config", config_path],
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "TOOLKIT_ALLOW_SCRIPT_SOURCE": "1"},
        check=False,
    )
    assert result.returncode == 0, f"Preflight fallito per {config_path}:\n{result.stderr[-500:]}"
