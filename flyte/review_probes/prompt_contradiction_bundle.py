"""Invariant probe: compiler-admitted contradiction bundles survive model assembly."""
# GOBBLER_REVIEW_TARGET selects the repository under test; test helper handles imports.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_review_prompts import PromptReview
case = PromptReview('test_admitted_contradiction_partner_reaches_prompt')
case.debug()
print('PASS: admitted contrast retained in captured prompt; no model call')
