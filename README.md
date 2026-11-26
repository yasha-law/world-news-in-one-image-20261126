# World News in One Image — 26 November 2026

A deterministic, standard-library-only Python program that sums up the world
news of **Thursday, 26 November 2026** in a single image.

This repository is the entry for the make.fun bounty
“Sum up 26 November's world news in one image”
(bounty page: https://make.fun/bounty/news-image-20261126).

## Run it

```sh
python3 main.py
```

- Writes `entry.png` to `/output/` when that directory exists and is
  writable, otherwise to the current directory.
- No network access, no third-party packages (Python 3.13 standard library
  only).
- Running it twice produces byte-identical output.

## Output rules (from the bounty)

- One PNG image, at most 1024 × 1024 px and at most 1 MiB.
- The program must run offline in a fresh container
  (1 CPU, 512 MB RAM, 60 s).

## Status

- Draft program and draft image are in place (headlines as of the morning
  of 26 Nov 2026, Asia/Shanghai).
- Final pass scheduled for 27 Nov 2026: refresh the headlines with the
  full day of 26 Nov news, regenerate, and verify determinism before
  submitting.

## How this repo is worked on

Humans and AI coding agents collaborate here through issues, branches and
pull requests. Every agent must read [AGENTS.md](AGENTS.md) before making
changes.

## License

MIT — see [LICENSE](LICENSE).
