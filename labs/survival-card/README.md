# Survival-card decks

The five decks printed on
[`docs/reference/ngspice-errors.md`](../../docs/reference/ngspice-errors.md) — the
ngspice survival card. Every number on that page comes out of this directory, and
`make` checks each one, so the page cannot drift away from what ngspice actually does.

This is not a lab. There is nothing to design and nothing to hand in. It exists so
that no page in AD103 ever tells you to retype a deck.

```bash
cd labs/survival-card
make            # all five decks and a verdict, about 14 seconds
```

Runs in a bare `hpretl/iic-osic-tools:2026.04` container with no environment setup.

## Files

| File | The page section it belongs to |
|---|---|
| `spice/dc_id_vgs.spice` | **2. `.dc`** — sweep a source. 181 rows, three `meas` lines |
| `spice/dc_family.spice` | **2. `.dc`** — a second, outer sweep: 905 rows in *one* vector |
| `spice/tran_rc.spice` | **3. `.tran`** — an RC charging, and the 1 ns edge you must subtract |
| `spice/ac_rc.spice` | **4. `.ac`** — the same RC in frequency |
| `spice/rc_parts.spice` | **"The two analyses have to agree"** — the $R$ and the $C$ on their own |
| `src/check.py` | The verdict, plus the three-way $R$ / $C$ / $\tau$ closure |

The `.op` deck from section 1 is not duplicated here — it is
[`labs/lab-01-first-schematic/spice/nmos_op.spice`](../lab-01-first-schematic/spice/nmos_op.spice),
which you have already run.

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

That last block is the habit the page is really teaching: **whenever you have an RC,
you have three numbers and any two of them give you the third for free.** Two
analyses and one hand calculation agreeing to four figures is what "the deck is
right" looks like.
