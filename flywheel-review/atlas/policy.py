"""Judgments the Atlas makes that are not measurements. Kept in one small file so the owner can change them."""


def kickoff_rank(direct_hits, failure_hits, has_code_check):
    """Order of the laws in a `laws-for` answer; the highest comes first.

    direct_hits     how many of the asked terms occur in the law's own text
    failure_hits    how many failure modes linked to the law match the terms
    has_code_check  True when chapter 02 names a mechanical check for the law

    TODO(owner): this default is a guess about where an agent's attention should go at kickoff. It puts a law that
    names the term first, then laws with matching failures, and it lifts a law that has no mechanical check by one
    step, on the view that only attention can catch what no gate catches. Other defensible choices: rank by recorded
    cost, by recurrence, or put process-only laws last because the agent cannot act on them. Five lines; yours.
    """
    return 3 * direct_hits + failure_hits + (0 if has_code_check else 1)
