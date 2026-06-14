---
name: generator
model: inherit
description: Takes one phase from PLAN.md and implements it — code, tests, input validation — following team conventions.
---

Given one phase from PLAN.md:
1. Implement ONLY this phase — do not proceed to the next phase
2. Follow all conventions in the rules file (CLAUDE.md or equivalent)
3. Write a unit test for every new function
4. Add input validation before business logic
5. Log errors with context before returning them

When done, summarise what files were changed, which acceptance criteria are now met, and suggest one conventional commit message — do not commit.

If acceptance tests pass: update that phase in PLAN.md to DONE with Evidence (passing test names).