# Contributing

Thanks for improving materials for the **UofT ASIC Team**.

## After creating a course from this template

1. Run `scripts/init-template.py` with `--id`, `--title`, and `--description` (org is always `uoftasic`).
2. Enable GitHub Pages: branch `main`, folder `/docs`.
3. Prefer repo names that match course ids (`dd103`, `ic101`, …).

See [TEMPLATE.md](TEMPLATE.md).

## Placeholders

Only these three are fillable:

| Token | Example |
|-------|---------|
| `ad103` | `dd103` |
| `AD103 — Nonlinear Circuits` | `DD103 — RTL on FPGAs & ASICs` |
| `The diode and the MOSFET in XSchem: regions of operation, and what the parameters mean.` | `RTL synthesis intro with Yosys` |

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

Do not put grades, solution keys, or PII under `docs/`. Prefer `labs/**/solutions/` and gitignore them on student forks when needed.

## Local docs preview

```bash
quarto preview docs
```

## Pull requests

Keep changes focused. For doc-only PRs, check navigation and math locally when practical. Optional CI may link-check `docs/**`.
