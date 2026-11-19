"""Unchosen source and receipt controls; no network access is performed."""
from pathlib import Path
import pytest

raise SystemExit(pytest.main([str(Path(__file__).resolve().parents[1] / "flyte/tests/test_review_assayer.py"),
                             "-q", "-k", "egress"]))
