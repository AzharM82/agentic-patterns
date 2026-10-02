"""Verify an automated change by re-running the check that justified it.

The whole technique is one line: after the change lands, call the *same* check
again. Everything else here is bookkeeping around that.

It exists because an agent that reports success is reporting on its own work.
Where an agent matches on the text of a finding rather than the condition the
finding describes, those two come apart exactly in the cases that matter - and
the ones that matter are the ones that reopen quietly a day later.

Standard library only. Python 3.11+.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Protocol

log = logging.getLogger(__name__)


class Check(Protocol):
    """Anything that can answer "is this condition satisfied right now?"

    Keep it cheap and keep it honest. A scanner query, a test, an HTTP call.
    What it must not be is a report from whatever made the change.
    """

    def __call__(self) -> bool: ...


@dataclass(frozen=True)
class Outcome:
    attempted: bool
    verified: bool
    reason: str
    checked_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

    @property
    def closable(self) -> bool:
        """Only a real fail-to-pass transition closes a finding.

        Note that `attempted=False, verified=True` is not closable here: if it
        was already passing, there was nothing to fix, and recording a fix is
        how phantom remediation numbers get into dashboards.
        """
        return self.attempted and self.verified


def verified_change(check: Check, apply: Callable[[], None],
                    *, retries: int = 0) -> Outcome:
    """Apply a change only if it is needed, then prove it worked.

    Args:
        check:   returns True when the condition is already satisfied.
        apply:   performs the change. Its return value is deliberately ignored.
        retries: extra attempts if verification fails. Default 0, because a
                 change that did not work the first time usually needs a human,
                 not another go.

    Returns:
        An Outcome. Close the finding only on `outcome.closable`.
    """
    if check():
        # Nothing to do. Saying so explicitly stops a no-op being recorded as
        # a successful remediation, which is the quiet way these numbers rot.
        return Outcome(False, True, "already satisfied; no change attempted")

    for attempt in range(retries + 1):
        apply()

        # The point of the whole module: ask the original question again,
        # rather than believing whatever just claimed to answer it.
        if check():
            return Outcome(True, True, f"verified after attempt {attempt + 1}")

        log.warning("change applied but check still fails (attempt %d)", attempt + 1)

    return Outcome(True, False,
                   f"check still failing after {retries + 1} attempt(s); needs a human")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # A change that works.
    state = {"patched": False}
    print(verified_change(lambda: state["patched"],
                          lambda: state.update(patched=True)))

    # A change that reports success and does nothing - the case this catches.
    print(verified_change(lambda: False, lambda: None))

    # Nothing to fix.
    print(verified_change(lambda: True, lambda: None))
