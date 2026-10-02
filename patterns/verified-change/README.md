# verified-change

**Problem.** An agent reads a finding, changes some code, and reports success. The finding
reopens on the next scan. Nobody notices for days, because the dashboard counts changes made
rather than conditions actually resolved.

It happens because the agent matches on the *text* of the finding, not the *condition* the
finding describes. Those two come apart precisely in the cases that matter.

**The obvious approach, and why it fails.** Trust the agent's report. You are then asking a
system to grade its own work on exactly the dimension where it is weakest.

## The pattern

1. Capture the check as a callable before anything acts on it.
2. Confirm it currently fails, so a no-op cannot look like a success.
3. Apply the change.
4. Re-run **the same callable**.
5. Close the finding only on a genuine fail-to-pass transition.

Step 4 is the technique. Steps 1, 2 and 5 are what stop the numbers rotting.

## Use it

```python
from verified_change import verified_change

outcome = verified_change(
    check=lambda: scanner.finding_is_resolved(finding_id),
    apply=lambda: agent.remediate(finding_id),
)

if outcome.closable:
    tracker.close(finding_id)
else:
    tracker.escalate(finding_id, outcome.reason)
```

```bash
python verified_change.py     # worked examples
python -m pytest              # tests
```

## What to decide differently

- **What `check` is.** The cheapest honest signal you have. If the only available check is the
  agent's own output, this pattern cannot help you — fix that first.
- **What happens on a verified failure.** Retry, escalate, or reopen. The default is zero
  retries, because a change that did not work usually needs a person rather than another go.
- **Where the outcome is recorded.** An unrecorded verification is the same as no verification.

## When not to use it

- When re-running the check costs more than the change itself.
- When the check is non-deterministic. A flaky check turns this into noise, and noise trains
  people to ignore the signal — worse than not having it.
- When the condition cannot be observed from outside the thing that changed it.
