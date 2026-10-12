# Law as Code in Practice: German Housing Benefit (Wohngeld) — case packages

The case packages of the book *Law as Code in Practice: German Housing Benefit (Wohngeld)*
(Law as Code by Country · Volume 2). The folder holds four fictional files over the same model — the facts,
the legal date and saved questions (`queries/`) of the Vogt family in Weimar, whose numbers are those of the
BMWSB worked example *Rechenbeispiel 7* (as of 1 January 2025). The rules are not copied here: `law.lock` pins
the German canons (`de.social.wohngeld`, `de.social.wohngeld_verordnung`, `de.tax.income_for_wohngeld`) by exact
version and hash in the Arxo registry, and `law install` fetches them.

**Status: private staging.** The canons are published in the private registry `arxohq/registry-staging` with
the layout of the public Arxo registry. Both repositories become public with the book.

## Run the example

```sh
git clone git@github.com:arxohq/registry-staging.git registry
git clone git@github.com:arxohq/law-as-code-germany-examples.git examples
cd examples/familie-weimar
law install --registry arxo=../../registry
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
law install --registry arxo=../../registry
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

Chapters 1, 5, 7 and 8 also run scenarios of the canon itself (`tests/*.lawtest`). Their sources are published
with the canon in the registry for reading; running them needs the pinned legal texts, which the registry does not
republish, so in this edition they run from a checkout of the Arxo repository (Appendix D of the book).
