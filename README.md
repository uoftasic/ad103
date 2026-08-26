# AD103 — Nonlinear Circuits

The diode and the MOSFET in XSchem: regions of operation, and what the parameters mean.

The third course in the UofT ASIC Team **analog track**. Published docs live under `./docs` and are served by GitHub Pages; the runnable XSchem/ngspice packages live in `labs/`.

Org: [github.com/uoftasic](https://github.com/uoftasic)

## Live docs

**This course:** https://uoftasic.com/ad103/

**Education hub:** https://edu.uoftasic.com/

**Prerequisites:** [IC101](https://uoftasic.com/ic101/) → [AD101](https://uoftasic.com/ad101/) → [AD102](https://uoftasic.com/ad102/), in that order.

## Template provenance

AD103 was created from [uoftasic/course-template](https://github.com/uoftasic/course-template). The rest of this
section is the template's own bootstrap documentation, kept for maintainers.

1. On [uoftasic/course-template](https://github.com/uoftasic/course-template), click **Use this template** → create a repo named after the course id (e.g. `dd103`, `serdes-lab`).
2. Clone and bootstrap:

```bash
python3 scripts/init-template.py \
  --id ad103 \
  --title "AD103 — Nonlinear Circuits" \
  --description "The diode and the MOSFET in XSchem: regions of operation, and what the parameters mean."
```

3. Enable **Settings → Pages → Deploy from a branch → `main` / `/docs`**.

See [TEMPLATE.md](TEMPLATE.md) for the checklist. Org is always `uoftasic` — only course id / title / description are filled in.

## Quick start

Every package under `labs/` runs with `make` alone, in a bare container, with no environment setup — each package pins its own PDK and model paths and ends in `PASS` or `FAIL` with a reason.

```bash
git clone https://github.com/uoftasic/ad103.git
cd ad103

docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work \
  hpretl/iic-osic-tools:2026.04 --skip \
  bash -c 'cd /work/labs/lab-01-first-schematic && make'
```

Docs preview (requires Node.js):

```bash
npx docsify-cli serve docs      # -> http://localhost:3000
```

Tool-heavy courses that need IIC-OSIC-TOOLS / SKY130 should document the team workbench setup in-course rather than bundling Docker in every repo.

## Layout

| Path | On Pages? | Purpose |
|------|-----------|---------|
| `docs/` | **Yes** | Human-facing Docsify site |
| `docs/labs/` | Yes | Lab *writeups* (procedure, theory) |
| `labs/` | No | Runnable packages (HDL, Python, data, graders) |
| `scripts/` | No | Team utilities / automation |
| `notebooks/` | No | Exploratory / assignment notebooks |
| `data/`, `figures/` | No | Shared datasets / source figures |

## GitHub Pages

| Setting | Value |
|---------|--------|
| Source | Deploy from a branch |
| Branch | `main` |
| Folder | `/docs` |

No Actions deploy step is required for the baseline Docsify site.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — Copyright UofT ASIC Team / `uoftasic`
