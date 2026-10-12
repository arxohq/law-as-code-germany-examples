# Law as Code in Practice: German Housing Benefit (Wohngeld) — case packages

The case packages of the book *Law as Code in Practice: German Housing Benefit (Wohngeld)*
(Law as Code by Country · Volume 2). The folder holds four fictional files over the same model — the facts,
the legal date and saved questions (`queries/`) of the Vogt family in Weimar, whose numbers are those of the
BMWSB worked example *Rechenbeispiel 7* (as of 1 January 2025). The rules are not copied here: `law.lock` pins
the German canons (`de.social.wohngeld`, `de.social.wohngeld_verordnung`, `de.tax.income_for_wohngeld`) by exact
version and hash, and `law install` fetches them from the canon repository `arxohq/arxo-wohngeld`.

> **First of all, a demonstration.** These files show what modelling legislation with Arxo can do. They do not
> claim legal accuracy or completeness, they are not an implementation by or for any German authority, and their
> answers are not legal advice.

**Status: private staging.** This repository and `arxohq/arxo-wohngeld` become public with the book.

## Run the example

```sh
git clone git@github.com:arxohq/arxo-wohngeld.git
git clone git@github.com:arxohq/law-as-code-germany-examples.git examples
cd examples/familie-weimar
law install --registry arxo=../../arxo-wohngeld/registry
law ask . --case Familie2025 --query-json queries/wohngeld-485.json --out "$(mktemp -d)"
```

`law install` never picks versions: it restores exactly what `law.lock` pins and checks every hash.
The `law` tool must execute `law.core/0.2.11`. `check.py` in the folder is the authors' check inside the Arxo
repository and is not needed to run the example.

## Cases and questions

| Case (`--case`) | Legal date | What it shows |
|---|---|---|
| `Familie2025` | 1 January 2025 | €1,710.00 income, €777.80 rent taken into account, €485 a month, claim established |
| `Familie20241231` | 31 December 2024 | the same family on the day before the update: €463 |
| `FamilieOhneWuerdigung` | 1 January 2025 | the amount is established; the claim waits for the Wohngeldbehörde's assessment (§ 21 Nr. 3) |
| `AlleinGrundsicherung` | 1 March 2025 | a single person receiving SGB II support with housing costs: excluded (§ 7), no claim (§ 21 Nr. 2) |

Saved questions: `einkommen-1710`, `miete-777-80`, `wohngeld-485`, `wohngeld-463`, `anspruch-485`,
`kein-anspruch-alle-ausgeschlossen`.

## One fact changed: `familie-weimar-varianten/`

The variations of Chapters 2, 3, 4 and 8 — the Vogts' case with one fact changed — are five cases of their own:

| Case (`--case`) | Change against `Familie2025` | Answer |
|---|---|---|
| `VMiete850` | rent €850 instead of €580 | M €998.20, Wohngeld €644 |
| `VSteuer` | income tax also expected (§ 16, three deductions) | Y €1,496.25, Wohngeld €542 |
| `VWerbung2000` | proven work expenses €2,000 instead of the flat rate | Y €1,658.6666666667, Wohngeld €499 |
| `VOhneMittelpunkt` | the flat is not established as the centre of Markus's life | 3 members, Y €1,600.00, M €750.20, Wohngeld €351 |
| `V20270101` | legal date 1 January 2027 | no amount: `MISSING_PARAMETER_VALUE` |

Its questions (`queries/collect-*.json`) collect the value instead of testing one:

```sh
cd examples/familie-weimar-varianten
law install --registry arxo=../../arxo-wohngeld/registry
law ask . --case VMiete850 --query-json queries/collect-w.json --out "$(mktemp -d)"
```

## Chapters and questions

| Chapter | Case and question |
|---|---|
| 0, 3 | `Familie2025` with every question; the table of Chapter 3 §5 — `familie-weimar-varianten` |
| 1 | `Familie20241231` / `wohngeld-463` and `Familie2025` / `wohngeld-485` |
| 2 | `Familie2025` / `einkommen-1710`, `miete-777-80` |
| 4, 9 | `Familie2025` / `wohngeld-485` (the proof carries z4 and the rows of Anlage 2) |
| 6 | `FamilieOhneWuerdigung` / `wohngeld-485`, `anspruch-485` |
| 7 | `AlleinGrundsicherung` / `kein-anspruch-alle-ausgeschlossen`, `wohngeld-485` |

## Chapters 1, 5, 7 and 8: the scenarios of the canon

These chapters also run scenarios of the canon itself (`tests/*.lawtest`). In `arxo-wohngeld` the canon is a
folder of `packages/` with its dependencies pinned inside it — nothing to install:

```sh
cd arxo-wohngeld/packages/de.social.wohngeld
law test . --file tests/bmwsb-2025.lawtest
```

In the book's commands, `<canon>` is this folder (`.` once you are inside it). The files the chapters name are
`bmwsb-2025`, `redaktionen` (Chapters 1, 5, 8), `tatsachen`, `ausschluss-und-urteil` (Chapters 7, 8). On
12 October 2026 all 87 scenarios of the canon passed in `arxo-wohngeld` with the released `law` 0.2.2.

## The saved answers of Chapter 9

`familie-weimar/runs/` holds the two answers of Chapter 9, saved with `--out`:

| Folder | Case / question | `result.json` (SHA-256) |
|---|---|---|
| `runs/familie-2025` | `Familie2025` / `wohngeld-485` — €485 | `e5ce59dd0f27c666410c9d247fad47b9ed75a939b052e360cb64fb6fe6790eb4` |
| `runs/familie-20241231` | `Familie20241231` / `wohngeld-463` — €463 | `f685d323d60ca09fbadd2be9940e09a7855fa3b0b4e593b0bf90c25d8b3f1735` |

| Fingerprint | `Familie2025` | `Familie20241231` |
|---|---|---|
| program (`manifest.programHash`) | `sha256:8a69e9ad8320d428a783c2a2e40bb0de53eb469ff99427bad732eaa21d0b749c` | the same |
| case (`manifest.caseHash`) | `sha256:8eb8b74380524355eada4c2c6b4811dc2e7a1fe166ce166dd94283d27ccf3f22` | `sha256:cba339409be3cd65a5b4701157e4a8331a7a265b2fa02a6e0a33c0b165e59bbc` |
| semantics | `law.core/0.2.11` | `law.core/0.2.11` |

Replay one in a copy and compare the bytes:

```sh
cp -R runs/familie-2025 /tmp/familie-2025
law eval /tmp/familie-2025
shasum -a 256 runs/familie-2025/result.json /tmp/familie-2025/result.json
```

The answers were recorded on 12 October 2026 with `law` 0.2.1 built from the Arxo repository at commit
`ba9c096f1d`; on that day both replays were byte for byte identical to the saved `result.json`.
