# AD103 — Nonlinear Circuits

The diode and the MOSFET in XSchem: regions of operation, and what the parameters mean.

The third course in the UofT ASIC Team **analog track**. The published docs live under `./docs` and are served by GitHub Pages; the runnable XSchem/ngspice packages live in `labs/`. Students start at the Course path on the course home page.

Org: [github.com/uoftasic](https://github.com/uoftasic)

## Live docs

**This course:** https://uoftasic.com/ad103/

**Education hub:** https://edu.uoftasic.com/

**Prerequisites:** [IC101](https://uoftasic.com/ic101/) → [AD101](https://uoftasic.com/ad101/) → [AD102](https://uoftasic.com/ad102/), in that order.

## Quick start

Every package under `labs/` runs with `make` alone, in a bare container, with no environment setup. Each package pins its own PDK and model paths and ends in `PASS` or `FAIL` with a reason.

```bash
git clone https://github.com/uoftasic/ad103.git
cd ad103

docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work \
  hpretl/iic-osic-tools:2026.08 --skip \
  bash -c 'cd /work/labs/lab-01-first-schematic && make'
```

Docs preview (requires Node.js):

```bash
npx docsify-cli serve docs      # -> http://localhost:3000
```

Students run the labs in the team workbench set up in [IC101](https://uoftasic.com/ic101/); Lab 01, Part 1 loads the course into it. The `docker run` line above is for checking a package without the workbench.

## Layout

| Path | On Pages? | Purpose |
|------|-----------|---------|
| `docs/` | **Yes** | Human-facing Docsify site |
| `docs/guide/` | Yes | Guide pages: reading only |
| `docs/labs/` | Yes | Lab *writeups*: where students run things |
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
