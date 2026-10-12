# Семья в Веймаре: Wohngeld 2024 против 2025, исключение и суждение органа

Четыре самостоятельных дела над `de.social.wohngeld@0.1.0` и его импортами
`de.social.wohngeld_verordnung@0.1.0` и `de.tax.income_for_wohngeld@0.1.0`.
Нормы, Anlagen и Mietenstufen остаются у канона; в примере — только факты дел
и вопросы. Дела порождает `corpus/laws/de/wohngeld/tools/build_example.py` из
тех же описаний, что сценарии канона.

## Дела

| Дело (`--case`) | Что предъявлено | Ответ и основание |
|---|---|---|
| `Familie2025` | BMWSB 2025, Rechenbeispiel 7: супруги с двумя детьми, Weimar (Mietenstufe III), брутто 2 240 € в месяц, Bruttokaltmiete 580 €, орган злоупотребления не установил; `legal_time` 01.01.2025 | `einkommen-1710`, `miete-777-80`, `wohngeld-485`, `anspruch-485`: `TRUE_ONLY` — числа PDF; параметры Anlage 2 — строка `#2025-01-01` (2. WoGFV) |
| `Familie20241231` | те же факты, `legal_time` 31.12.2024 | `wohngeld-463`: `TRUE_ONLY` (Anlagen 2023 года, § 44 Abs. 1 WoGG); `wohngeld-485`: `NEITHER`; строка `#2023-01-01` (Wohngeld-Plus-Gesetz) |
| `FamilieOhneWuerdigung` | та же семья на 01.01.2025, Wohngeldbehörde § 21 Nr. 3 не оценивала | `wohngeld-485`: `TRUE_ONLY`; `anspruch-485`: `NEITHER` / `REQUIRES_JUDGMENT`, запрос `missbraeuchliche_inanspruchnahme` |
| `AlleinGrundsicherung` | одинокое лицо с трансфером SGB II и Kosten der Unterkunft | `kein-anspruch-alle-ausgeschlossen`: `TRUE_ONLY` (§ 7 Abs. 1 S. 1 Nr. 1, § 21 Nr. 2); `wohngeld-485`: `NEITHER` |

Ожидания взяты из PDF BMWSB и текста закона, а не из ответа движка: 463 € —
арифметика Anlagen 2023 года (`corpus/laws/de/wohngeld/tools/reference_calc.py`,
z4 = 463,2504131300). Все дела пользуются одними идентификаторами
домохозяйства, поэтому каждый вопрос из [`queries/`](queries/) подходит к любому
делу.

## Запуск из корня checkout

Python 3.12 или новее. Зависимости восстанавливаются по `law.lock`. Если общий
`corpus/clir` уже содержит порождённые координатором CLIR трёх пакетов с теми же
хэшами, флаг `--clir` не нужен; иначе берётся частный снимок профиля набора:

```sh
.venv-work-profile/bin/python verify/ci/tools/work_profile.py --build-only \
  --config verify/ci/data/work-profiles/oecd-wohngeld.toml --output /tmp/wohngeld-snap
.venv-work-profile/bin/python packs/examples/cases/materialize_deps.py \
  corpus/laws/de/wohngeld/examples/familie-weimar --clir /tmp/wohngeld-snap/clir
```

Задать вопрос и сохранить ответ с доказательством:

```sh
./law ask corpus/laws/de/wohngeld/examples/familie-weimar \
  --case Familie2025 \
  --query-json corpus/laws/de/wohngeld/examples/familie-weimar/queries/wohngeld-485.json \
  --out /tmp/wohngeld-runs/familie-2025
```

Смена редакции: тот же вопрос для `--case Familie20241231` даёт `NEITHER`, а
`queries/wohngeld-463.json` — `TRUE_ONLY`. В `result.json` → `proofGraph` у
применений формулы атрибут `a3Selections` называет выбранные строки параметров
(`…WertBMitglieder4#2025-01-01` против `…#2023-01-01`); их якоря
(`ZWEITE_WOGFV_ANLAGEN_1_3`, `WPG_ANLAGEN_2_3`) лежат в `request.json` →
`ir.nodes`.

Суждение органа:

```sh
./law ask corpus/laws/de/wohngeld/examples/familie-weimar \
  --case FamilieOhneWuerdigung \
  --query-json corpus/laws/de/wohngeld/examples/familie-weimar/queries/anspruch-485.json
```

Повтор сохранённого расчёта без исходников:

```sh
./law eval /tmp/wohngeld-runs/familie-2025
```

## Проверить подборку

```sh
.venv-work-profile/bin/python corpus/laws/de/wohngeld/examples/familie-weimar/check.py
```

Для каждого из одиннадцати вопросов скрипт сверяет:
- статус вычисления и истинности, а также запросы суждения;
- применение решающего правила и его якорь в редакции даты;
- выбранную строку параметра Anlage 2 и её якорь на выпуск BGBl (для двух дат);
- канонические ответы Rust и Python;
- replay (`law eval`) и повторный `ask` — байт в байт.

`deps/` и `runs/` в Git не хранятся. Регистрация примера в общих воротах —
у координатора.
