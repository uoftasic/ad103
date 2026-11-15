# Survival-card decks

This directory holds the five decks printed on the ngspice survival card,
[`docs/reference/ngspice-errors.md`](../../docs/reference/ngspice-errors.md). Every number on that
page comes out of these decks, and `make` checks each one against the value the page prints, so the
page can't drift away from what ngspice actually does.

Although it sits under `labs/`, this is not a lab: you have nothing to design and nothing to hand
in. It's here so that no page in AD103 ever asks you to retype a deck.

```bash
cd labs/survival-card
make            # all five decks and a verdict, about 50 seconds
```

It runs in a bare `hpretl/iic-osic-tools:2026.08` container with no environment setup, because
the image already has `PDK_ROOT` at `/foss/pdks` (and the `Makefile` pins it there anyway).

| Command | What it does |
|---|---|
| `make` | run all five decks and print a verdict |
| `make dc` | `.dc`: sweep a source |
| `make tran` | `.tran`: the time domain |
| `make ac` | `.ac`: the frequency domain |
| `make parts` | the R and the C on their own, so the arithmetic can close |
| `make clean` | delete the logs in `results/` |

## Files

| File | The page section it belongs to |
|---|---|
| `spice/dc_id_vgs.spice` | **2. `.dc`**: sweep a source. 181 rows, three `meas` lines |
| `spice/dc_family.spice` | **2. `.dc`**: a second, outer sweep, 905 rows in *one* vector |
| `spice/tran_rc.spice` | **3. `.tran`**: an RC charging, and the 1 ns edge you must subtract |
| `spice/ac_rc.spice` | **4. `.ac`**: the same RC in frequency |
| `spice/rc_parts.spice` | **"The two analyses have to agree"**: the $R$ and the $C$ on their own |
| `src/check.py` | the verdict, plus the three-way $R$ / $C$ / $\tau$ check |

The `.op` deck from section 1 isn't repeated here, because you have already run it in Lab 01:
it's [`labs/lab-01-first-schematic/spice/nmos_op.spice`](../lab-01-first-schematic/spice/nmos_op.spice).

## Reference output

```
  ok  dc rows                           181   (page 181)
  ok  id_1v8 (A)               6.962750e-04   (page 6.962750e-04)
  ok  id_0v9 (A)               6.387600e-05   (page 6.387600e-05)
  ok  vg_at_1ua (V)            5.658150e-01   (page 5.658150e-01)
  ok  dc family rows                    905   (page 905)
  ok  id[180] (A)              2.005399e-06   (page 2.005399e-06)
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
