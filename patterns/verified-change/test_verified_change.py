from verified_change import verified_change


def test_a_change_that_works_is_closable():
    state = {"patched": False}
    out = verified_change(lambda: state["patched"], lambda: state.update(patched=True))
    assert out.attempted and out.verified and out.closable


def test_a_change_that_reports_success_and_does_nothing_is_caught():
    """The case the pattern exists for."""
    out = verified_change(lambda: False, lambda: None)
    assert out.attempted and not out.verified and not out.closable
    assert "needs a human" in out.reason


def test_nothing_to_fix_is_not_recorded_as_a_fix():
    """attempted=False must never be closable, or no-ops inflate the numbers."""
    out = verified_change(lambda: True, lambda: None)
    assert out.verified and not out.attempted and not out.closable


def test_retries_stop_at_the_first_verified_pass():
    calls = {"apply": 0}
    state = {"patched": False}

    def apply():
        calls["apply"] += 1
        if calls["apply"] == 2:          # fails once, works on the retry
            state["patched"] = True

    out = verified_change(lambda: state["patched"], apply, retries=3)
    assert out.closable
    assert calls["apply"] == 2           # stopped as soon as it verified
