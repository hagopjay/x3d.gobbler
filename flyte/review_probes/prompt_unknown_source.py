"""Invariant probe: unconfigured source text cannot reach model adapter."""
# GOBBLER_REVIEW_TARGET selects the repository under test; test helper handles imports.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_review_prompts import PromptReview
case = PromptReview('test_unknown_source_cannot_reach_model')
case.debug()
print('PASS: unknown source rejected before model prompt; no model call')
