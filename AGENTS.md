# Agent guide — UofT ASIC course repos

You are working in a **course repository** for the UofT ASIC Team (`uoftasic`): pedagogical materials for IC / RTL / FPGA / open-source ASIC flows. The site under `docs/` is built with Quarto and published on GitHub Pages by `.github/workflows/site.yml`. Runnable work lives outside `docs/`.

Optimize for **clear student learning paths**, not template maintenance. Prefer concrete labs and notes students can follow end-to-end over meta documentation.

## Goals

- Teach IC development skills: RTL (SystemVerilog/Verilog), simulation, synthesis, FPGA bring-up, and/or open ASIC flows (e.g. Yosys, LibreLane, SKY130) as the course requires.
- Keep each lab **self-contained**, in the lab shape described under [Lab writeup shape](#lab-writeup-shape) below.
- Keep guide pages (`docs/guide/`) **reading only**: concepts, figures, worked examples. Commands and activities belong in the lab writeups; a guide page points to the lab part where the student does it.
- Keep the **Course path** table on `docs/index.md` (alternating Read and Do rows, with time estimates, in the format under [Course path table](#course-path-table)), the sidebar in `docs/_quarto.yml` and the chapter list in `docs/_quarto-pdf.yml` in the same order.
- Separate **what students read** (`docs/`) from **what they run** (`labs/`, `scripts/`, `notebooks/`).
- Never publish grades, solution keys, or PII under `docs/`. Put keys in `labs/**/solutions/` and gitignore them on student forks when policy requires.

## Layout (do not fight this)

| Path | Published? | Put here |
|------|------------|----------|
| `docs/` | Yes | Guides, lab writeups, figures for the site |
| `docs/guide/` | Yes | Conceptual notes (flows, tools, theory) |
| `docs/labs/` | Yes | Lab writeups only (`lab-NN-*-overview.md`) |
| `docs/assets/img/` | Yes | Small diagrams / waveforms for docs |
| `labs/<lab-id>/` | No | HDL, Python, testbenches, local data, graders |
| `scripts/` | No | Course utilities / automation |
| `notebooks/` | No | Exploratory or assignment notebooks |
| `data/`, `figures/` | No | Shared datasets / source figures |

Site wiring: `docs/_quarto.yml` (site, sidebar, navbar, per-page PDFs), `docs/_quarto-pdf.yml` (the whole course as one PDF) and `docs/_filters/course.lua` (turns `<details>` answers into collapsible callouts, and moves them to an Answers section at the end of each page in PDFs). Math: `$inline$`, `$$display$$`.

## Adding a lab (preferred unit of coursework)

Lab IDs: `lab-NN-short-name` (e.g. `lab-02-counter-sv`).

1. Create `labs/<lab-id>/` with at least:
   - `README.md` — points at the writeup on the site and how to run
   - `src/` — HDL / Python / entrypoints
   - `data/` — small inputs (large binaries → Git LFS or external)
   - `requirements.txt` or tool notes when needed
2. Add `docs/labs/<lab-id>-overview.md` in the [lab writeup shape](#lab-writeup-shape), titled `# Lab NN: Title`.
3. Add a Do row for it to the Course path table in `docs/index.md` ([format](#course-path-table)), keep the course total on the home page equal to the sum of the row times, and add the writeup to the sidebar in `docs/_quarto.yml` and the chapters in `docs/_quarto-pdf.yml`, in the same position (and to the navbar in `_quarto.yml` only if it belongs in top nav).
4. Cross-link: writeup → GitHub `labs/<lab-id>/`; package README → `docs/labs/<lab-id>-overview.md`.

**Writeups teach; packages execute.** Do not dump long HDL into site pages — reference files under `labs/`.

### Lab writeup shape

1. What you'll build or measure (2–3 lines), the package link, **Before you start** (guide pages to read, setup), and **Time**. Leave optional parts out of the time, or give their time separately.
2. Numbered parts (`## Part 1: Label`). Each part opens with the one question it answers, has numbered steps (more than about eight means split or trim it), and ends in a **You should see** check with the observed numbers.
3. At least one required part where the student produces something: edits a deck or file, writes a test, draws a cell, or computes a number and writes it down before checking it. Ask for a prediction wherever one is reasonable.
4. When a check would also explain *why*, keep the numbers in the check and turn the explanation into a question with a collapsed answer directly under it:

   ```html
   <details>
   <summary>Answer</summary>

   The answer, with Markdown and $math$ as usual. Keep the blank lines.

   </details>
   ```

5. Optional parts go after the required ones, with `(optional)` in the header. No required part may depend on one.
6. **Finishing**, always in this order: **You're done when** (one checkable line about the student's own work, not the shipped `PASS`), **Questions** (each with a collapsed answer or a pointer to the step that answers it), **Submit** (what to submit, or "Nothing to submit.").
7. Then **Going further** (optional), and last the line `Next on the [Course path](../index.md#course-path): …`.

Lookup material (troubleshooting tables, warning catalogues, long tool output) goes on the course's reference pages, linked from the step where it comes up. Aim for at most about 2,500 words per writeup, without cutting teaching content to get there. Lab 01 Part 1 is "Load the course": a one-line pointer to IC101 Lab 03 for the workbench, then `.designinit`, `mod add <course>`, the tool versions the outputs depend on, and only the troubleshooting rows specific to this course.

### Course path table

```
| # | | What | Time |
|---|---|---|---|
| 1 | Read | [Page](guide/page.md) · [Page](guide/page.md) | 45 min |
| 2 | Do | [Lab 01: Title](labs/lab-01-...-overview.md). One sentence on what you'll do. | 1.5 h |
```

Read and Do are plain text, lab titles use a colon, and every Do row ends with one sentence on what you'll do. The row times add up to the total on the home page.

## Adding a guide page

1. Add kebab-case Markdown under `docs/guide/` (e.g. `yosys-synth.md`). Reading only: no required commands.
2. Add it to the right Read row of the Course path in `docs/index.md`, and add it to the sidebar in `docs/_quarto.yml` and the chapters in `docs/_quarto-pdf.yml` in the same position.
3. Images under `docs/assets/img/` with paths relative to `docs/`.
4. Link between pages with paths relative to the page you are writing in (`../guide/x.md` from a lab), as Quarto resolves them; use GitHub URLs for `labs/` and `scripts/`.

## Pedagogy checklist (use when authoring)

- State **learning objectives** in student language (“You will synthesize a counter and inspect the netlist”).
- Assume a clone of this repo and the course’s documented workbench; do not bundle Docker in every lab unless the course already does.
- For EDA-heavy work (LibreLane / SKY130 / IIC-OSIC-TOOLS), document the **team workbench** steps in-course rather than inventing a one-off container story.
- Keep procedures copy-pasteable (`cd`, install, simulate/synth, check artifact).
- Define **expected results** (printout, waveform check, area/timing ballpark, golden hash) so students know they succeeded.
- Progress difficulty across labs; reuse naming and directory conventions so later labs feel familiar.
- Prefer small, inspectable designs over opaque blobs; when using IP or PDK artifacts, keep secrets and huge binaries out of git.

## Tooling norms

- Python helpers and graders: under `labs/<id>/src/` or `scripts/`; list entry points in the nearest `README.md`.
- SystemVerilog/Verilog: under `labs/<id>/src/` (or `rtl/`, `tb/` if you split — stay consistent within the course).
- Heavy outputs (GDS, large FSDB/VCD, PDK caches): local `results/` or LFS — never under `docs/`.
- Preview docs locally: `quarto preview docs` → http://localhost:4200

## What not to do

- Do not add maintainer-only pages to the published site (contributing guides, template notes, notation stubs “for debugging”).
- Do not put solution keys or rubrics in `docs/`.
- Do not replace student-facing content with template/bootstrap instructions; point humans at `CONTRIBUTING.md` / `TEMPLATE.md` only when they are bootstrapping or changing repo conventions.
- Do not change org assumptions: GitHub org is `uoftasic`; course id matches the repo name.

## Quick references

- Repo conventions: `CONTRIBUTING.md`
- Bootstrap tokens / Pages checklist: `TEMPLATE.md`
- Sample lab shape: `labs/lab-01-first-schematic/` + `docs/labs/lab-01-first-schematic-overview.md`
