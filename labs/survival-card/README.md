# Survival-card decks

This directory holds the six decks printed on the ngspice survival card,
[`docs/reference/ngspice-errors.md`](../../docs/reference/ngspice-errors.md). `make` checks every
number those decks print on that page against the value the page shows, so the page can't drift
away from what ngspice actually does.

Although it sits under `labs/`, this is not a lab: you have nothing to design and nothing to hand
in. It's here so that no page in AD103 ever asks you to retype a deck.

```bash
cd labs/survival-card
make            # all six decks and a verdict, about a minute
```

It runs in a bare `hpretl/iic-osic-tools:2026.08` container with no environment setup, because
the image already has `PDK_ROOT` at `/foss/pdks` (and the `Makefile` pins it there anyway).

| Command | What it does |
|---|---|
| `make` | run all six decks and print a verdict |
| `make op` | `.op`: one bias point, and the small-signal parameters |
| `make dc` | `.dc`: sweep a source |
| `make tran` | `.tran`: the time domain |
| `make ac` | `.ac`: the frequency domain |
| `make parts` | the R and the C on their own, so the arithmetic can close |
| `make clean` | delete the logs in `results/` |

## Files

| File | The page section it belongs to |
|---|---|
| `spice/op_nmos.spice` | **1. `.op`**: one bias point, plus the `print` line for `vth`, `gm`, `gds` and `cgg` |
| `spice/dc_id_vgs.spice` | **2. `.dc`**: sweep a source. 181 rows, three `meas` lines |
| `spice/dc_family.spice` | **2. `.dc`**: a second, outer sweep, 905 rows in *one* vector |
| `spice/tran_rc.spice` | **3. `.tran`**: an RC charging, and the 1 ns edge you must subtract |
| `spice/ac_rc.spice` | **4. `.ac`**: the same RC in frequency |
| `spice/rc_parts.spice` | **"The two analyses have to agree"**: the $R$ and the $C$ on their own |
| `src/check.py` | the verdict, plus the three-way $R$ / $C$ / $\tau$ check |

The circuit in section 1 is the one you have already run in Lab 01,
[`labs/lab-01-first-schematic/spice/nmos_op.spice`](../lab-01-first-schematic/spice/nmos_op.spice).
`spice/op_nmos.spice` is that deck with the page's `print` line for the small-signal parameters
added, so that `make` can check those four numbers along with the drain current.

## Reference output

```
  ok  op i(vds) (A)           -5.010460e-04   (page -5.010460e-04)
  ok  op vth (V)               7.692674e-01   (page 7.692674e-01)
  ok  op gm (S)                5.322242e-04   (page 5.322242e-04)
  ok  op gds (S)               5.141539e-05   (page 5.141539e-05)
  ok  op cgg (F)               8.568632e-16   (page 8.568632e-16)
  ok  dc rows                           181   (page 181)
  ok  id_1v8 (A)               6.962750e-04   (page 6.962750e-04)
  ok  id_0v9 (A)               6.387600e-05   (page 6.387600e-05)
  ok  vg_at_1ua (V)            5.658150e-01   (page 5.658150e-01)
  ok  dc family rows                    905   (page 905)
  ok  id[180] (A)              2.005399e-06   (page 2.005399e-06)
  ok  id[181] (A)              1.881519e-42   (page 1.881519e-42)
  ok  tran rows                        8014   (page 8014)
  ok  tran tau (s)             3.108260e-09   (page 3.108260e-09)
  ok  tran vfinal (V)          1.800000e+00   (page 1.800000e+00)
  ok  ac rows                          1001   (page 1001)
  ok  ac f3db (Hz)             7.564490e+07   (page 7.564490e+07)
  ok  R (ohm)                  1.018463e+04   (page 1.018463e+04)
  ok  C_mim (F)                2.065822e-13   (page 2.065822e-13)

  R x C                    = 2.10396 ns   (arithmetic)
  1 / (2 pi R C)           = 75.6453 MHz (arithmetic)
  .ac measured             = 75.6449 MHz  (-0.0005 % from the arithmetic)
  .tran measured, minus the 1 ns edge = 2.10826 ns  (+0.204 % from the arithmetic)

PASS  every number on the survival card reproduces
```

The last block is the habit the page teaches: whenever you have an RC, you have three numbers, and
any two of them give you the third. Here the `.ac` result lands within 0.0005 % of the hand
calculation and the `.tran` result within 0.204 %, once you subtract the 1 ns edge. Two analyses
and one hand calculation that agree that closely are good evidence the decks are right.
