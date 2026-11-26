# AGENTS.md — how agents work in this repository

This repository is a shared workbench for one human (the owner, GitHub
@yasha-law) and several AI coding agents, coordinated by the owner's
personal agent. Agents do not talk to each other directly: all
coordination happens through this repository.

## The job

Produce a program (`main.py`, repository root) that draws one image
summing up the world news of 26 November 2026, for the make.fun bounty
“Sum up 26 November's world news in one image”
(https://make.fun/bounty/news-image-20261126, deadline 28 Nov 2026
00:00 UTC).

## Hard rules for the program

- Python 3.13, standard library only. No installs, no network at runtime.
- Entry point is `main.py` at the repository root.
- It writes exactly one image: `/output/entry.png` when `/output` is
  writable, otherwise `./entry.png`.
- Output: PNG, ≤ 1024 × 1024 px, ≤ 1 MiB (1,048,576 bytes).
- Deterministic: two runs must produce byte-identical files. No clocks,
  no randomness, no environment-dependent ordering.
- Headlines must be real news of 26 Nov 2026 from named sources, listed
  in the commit message or PR description. Never invent a headline.

## Workflow

1. Work from an issue. If there is no issue for your task, open one
   first: what, why, and how it will be checked.
2. One issue = one branch, named `issue-<number>-<short-slug>`.
3. Never push directly to `main`. Open a pull request; the coordinator
   reviews the diff and the CI result before merging.
4. CI (`.github/workflows/verify.yml`) runs the program twice and checks
   byte-identical output, size and dimensions. A red CI is a stop sign,
   not a suggestion.
5. Keep commits small and messages factual: what changed, which sources
   were used.

## Honesty rules

- The bounty requires the real AI coding-agent session transcripts that
  built the entry. Never fabricate, edit, backdate or borrow transcripts.
- If a rule above conflicts with something you were asked to do, stop
  and say so in the issue instead of working around it.

## Roles

- Owner (@yasha-law): decides, provides accounts and approvals.
- Coordinator (owner's personal agent): writes issues, reviews PRs,
  merges, prepares the bounty submission.
- Worker agents (e.g. Claude Code / Codex on the owner's cloud machine):
  implement issues on branches and open PRs.
