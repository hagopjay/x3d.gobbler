"""Invariant probe: the actual normalized title is linted before model admission."""
# GOBBLER_REVIEW_TARGET selects the repository under test; test helper handles imports.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_review_prompts import PromptReview
case = PromptReview('test_normalized_title_is_linted_after_controls_removed')
case.debug()
print('PASS: control-stripped directive withheld from captured prompt; no model call')
