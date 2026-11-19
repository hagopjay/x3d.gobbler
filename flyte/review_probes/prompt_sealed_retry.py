"""Invariant probe: sealed refusal cannot re-enter via immediate retry feedback."""
# GOBBLER_REVIEW_TARGET selects the repository under test; test helper handles imports.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_review_prompts import PromptReview
case = PromptReview('test_sealed_refusal_cannot_bypass_compiler_on_retry')
case.debug()
print('PASS: sealed refusal absent from immediate retry prompt; no model call')
