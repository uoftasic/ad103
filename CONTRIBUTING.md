# Contributing

Thanks for improving materials for the **UofT ASIC Team**.

## After creating a course from this template

1. Run `scripts/init-template.py` with `--id`, `--title`, and `--description` (org is always `uoftasic`).
2. Enable GitHub Pages with **Settings → Pages → Source: GitHub Actions**, so that `.github/workflows/site.yml` can build and deploy the site.
3. Prefer repo names that match course ids (`dd103`, `ic101`, …).

See [TEMPLATE.md](TEMPLATE.md).

## Placeholders

These three tokens are the only placeholders, and `scripts/init-template.py` fills them in:

| Token | Example |
|-------|---------|
| `ad103` | `dd103` |
| `AD103 — Nonlinear Circuits` | `DD103 — RTL on FPGAs & ASICs` |
| `Simulate diodes and MOSFETs with the SKY130 device models, and finish with a CMOS inverter that you draw in XSchem and size yourself.` | `RTL synthesis intro with Yosys` |

## Conventions

| Item | Convention |
|------|------------|
| Org | `uoftasic` |
| Default branch | `main` |
| Docs pages | kebab-case `.md` under `docs/` |
| Lab IDs | `lab-NN-short-name` |
| Adding a guide page | add `.md` under `docs/guide/` (reading only; activities go in a lab), add it to the Course path, add it to the sidebar in `docs/_quarto.yml` |
| Adding a lab | `labs/<id>/` + `docs/labs/<id>-overview.md` + a Course path row in `docs/index.md` + sidebar entry in `docs/_quarto.yml` (and a chapter in `docs/_quarto-pdf.yml`) in the same order |
| Lab writeup | titled `# Lab NN: Title`; parts open with a question and end in a "You should see" check; explanations go in `<details>` answers; ends with **You're done when** (the student's own work), **Questions**, **Submit**, then Going further and the "Next on the Course path" line. Full shape in [AGENTS.md](AGENTS.md#lab-writeup-shape) |
| Course path row | `\| 2 \| Do \| [Lab 01: Title](labs/...). One sentence on what you'll do. \| 1.5 h \|`, with plain Read/Do and row times that add up to the home page total |
| Binaries | small images in `docs/assets/`; large data → Git LFS or external |

## Docs vs labs

- **`docs/`** — published site. Lab *writeups* in `docs/labs/`.
- **`labs/`** — runnable HDL / Python / data. Each `labs/<id>/README.md` links to its writeup on the site.
- **`scripts/`** — utilities; list entry points in `scripts/README.md`.

Do not put grades, solution keys, or PII under `docs/`, because everything there is published. Put solution keys in `labs/**/solutions/` instead, and gitignore them on student forks when needed.

## Local docs preview

```bash
quarto preview docs
```

This serves a live preview of the site at http://localhost:4200.

## Pull requests

Keep each pull request focused on one change. For a doc-only PR, check the navigation and the math in a local preview when you can. A pull request that changes `docs/` runs two checks in CI:

- `.github/workflows/site.yml` renders the site with Quarto and runs `scripts/check_site.py` on it, which checks that every local link, image and `#anchor` resolves.
- `.github/workflows/docs-link-check.yml` runs lychee over the Markdown under `docs/`, which also checks external links, and checks that every image a page references exists on disk.
