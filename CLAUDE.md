# Working on ConductOS

Follow the Karpathy guidelines for all code in this repo:

1. **Think before coding.** State assumptions. If a request has more than one reading, lay them out instead of picking silently. Ask when something is unclear.
2. **Simplicity first.** Write the minimum code that solves the request. No speculative features, abstractions or configurability.
3. **Surgical changes.** Every changed line should trace to the request. Match the existing style. Remove only what your own change made unused. Mention unrelated dead code instead of deleting it.
4. **Goal-driven execution.** Turn each task into a verifiable goal, usually a test that fails first and then passes. State a short plan with a check for each step.

Repo facts:
- Run `pytest -q` before every push. CI runs it on every push to `main`.
- Product docs (PRDs, autonomy policy, decision log) live in Notion and are linked from `README.md`. Code that changes behavior governed by `policy/autonomy.yaml` needs a Decision Log entry.
- Never commit `.env` or secrets. The Jev key is `TYPESAFE_API_KEY`, in a GitHub Actions secret.
