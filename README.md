# AI-Augmented SWE Workflow — Labs

Student lab repo for the **AI-Augmented Engineering Workflow** course.

`main` is just this guide. The actual work starts on **`lab-01-start`**, which holds `requirements.pdf` **and a partially-built `state_machine/` codebase** — the project is already underway (the spec describes a partly-done engine). You build the docs and finish the code, lab by lab.

> This course uses **Cursor** as the reference AI tool. All demos and screenshots are Cursor. If you have Claude Code or another agent, the same tasks work there — setup is on you.

## Getting Started

```bash
git clone https://github.com/szeyu/ai-augmented-swe-workflow-labs.git
cd ai-augmented-swe-workflow-labs
git checkout lab-01-start  # requirements.pdf + the partial codebase
git checkout -b my-work    # work on your own branch from day 1
uv sync                    # set up the environment
uv run pytest -q           # baseline: evaluator tests pass, engine tests fail (expected)
```

Always work on `my-work` (or any branch name you prefer). Never commit directly to a checkpoint branch.

## Fell Behind? Catch Up Here

Checkpoint branches are **independent snapshots** — each carries the instructor's output through the previous lab. The codebase is present from `lab-01-start` onward, so catching up is always a single whole-branch checkout (no file cherry-picking):

```bash
git checkout lab-0X-start   # start lab X with everything through lab X-1 done
git checkout -b my-work-X    # keep working on your own branch
```

| I want to start... | Run this | Already done for you |
|--------------------|----------|----------------------|
| Lab 01 | `git checkout lab-01-start` | requirements.pdf + partial code |
| Lab 02 | `git checkout lab-02-start` | + `SPEC.md` |
| Lab 03 | `git checkout lab-03-start` | + AI-enriched `SPEC.md` |
| Lab 04 | `git checkout lab-04-start` | + `ARCHITECTURE.md` |
| Lab 05 | `git checkout lab-05-start` | + `PLAN.md` |
| Lab 06 | `git checkout lab-06-start` | + `.cursor/rules/` harness |
| Lab 07 | `git checkout lab-07-start` | + first TODO phase implemented |
| Lab 08 | `git checkout lab-08-start` | + subagents (`.cursor/agents/`) |
| Lab 09 | `git checkout lab-09-start` | + MCP setup (`.cursor/mcp.json`) |
| Finished project | `git checkout completed` | full reference implementation |

Your own work on `my-work` is never touched by switching branches.

## What You'll Build

| Lab | Artifact |
|-----|----------|
| 01 | `SPEC.md` |
| 02 | `SPEC.md` enriched via AI interview |
| 03 | `ARCHITECTURE.md` + Mermaid diagrams |
| 04 | `PLAN.md` |
| 05 | `.cursor/rules/` harness (the rules experiment) |
| 06 | First TODO phase implemented in `state_machine/` |
| 07 | Subagents (`.cursor/agents/`) |
| 08 | MCP setup (`.cursor/mcp.json`) |
| 09 | Skills (`.cursor/skills/`) |

End of course = a complete, working state machine engine you finished end-to-end using an AI-augmented workflow.
