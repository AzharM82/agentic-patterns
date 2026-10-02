# agentic-patterns

Small, runnable patterns for putting AI agents into production systems — the kind where being
approximately right is not good enough.

Each pattern is one directory: the problem, the mechanism, a reference implementation you can
read in a couple of minutes, and the honest limits. No framework, no install, no abstractions
you have to buy into. Copy the file, change the names, delete what you do not need.

## Patterns

| Pattern | The problem it solves |
|---|---|
| [verified-change](patterns/verified-change/) | An agent reports it fixed something; the finding reopens next scan |

## Why these exist

I lead engineering for AI automation at Microsoft, and most of what I learn the hard way is
about the gap between an agent that works in a demo and one you can let near production. The
interesting part is rarely the model. It is the loop around it: what the agent is allowed to
do, what it must prove, and what happens when it is confidently wrong.

These are the parts of that which generalise.

## Provenance

Everything here is written independently for this repository, as generic reference
implementations of general techniques. **No employer code, configuration, data or proprietary
material appears in this repo**, and nothing here is specific to any company's systems.

A pattern is an idea. The idea is what is shared; the implementation is written fresh.

## Using them

Python 3.11+, standard library only unless a pattern says otherwise.

```bash
git clone https://github.com/AzharM82/agentic-patterns
cd agentic-patterns/patterns/verified-change
python verified_change.py        # runs the worked example
python -m pytest                 # runs the tests
```

Issues and pull requests welcome, particularly cases where a pattern breaks.

## Licence

MIT — see [LICENSE](LICENSE). Use them, change them, ship them.
