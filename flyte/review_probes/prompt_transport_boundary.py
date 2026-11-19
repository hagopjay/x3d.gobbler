"""Invariant probe: model adapter refuses an accidentally uncompiled prompt."""
# GOBBLER_REVIEW_TARGET selects the repository under test; test helper handles imports.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_review_prompts import PromptReview
case = PromptReview('test_raw_transport_prompt_rejected_before_any_api')
case.debug()
print('PASS: raw-string prompt rejected before transport; no model call')
