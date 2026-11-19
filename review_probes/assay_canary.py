"""Real-instrument canary coverage/cache regressions; optional GOBBLER_REVIEW_TARGET selects baseline."""
from pathlib import Path
import pytest

raise SystemExit(pytest.main([str(Path(__file__).resolve().parents[1] / "flyte/tests/test_review_assayer.py"),
                             "-q", "-k", "canary"]))
