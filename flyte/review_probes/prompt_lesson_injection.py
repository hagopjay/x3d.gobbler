"""Invariant probe: validator-echoed instructions stay out of a later model prompt."""
# GOBBLER_REVIEW_TARGET selects the repository under test; test helper handles imports.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_review_prompts import PromptReview
case = PromptReview('test_persistent_validator_echo_is_quoted')
case.debug()
print('PASS: raw validator echo withheld from later captured prompt; no model call')
