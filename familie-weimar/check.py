#!/usr/bin/env python3
"""Четыре дела Wohngeld: статусы, решающие правила, выбранная редакция, Rust/Python, replay, повтор.

Запуск из checkout, Python >= 3.12, после материализации `deps/`
(`packs/examples/cases/materialize_deps.py <пакет> [--clir <каталог снимка>]`).

Ожидания — не ответы движка:
* 485 €, 1 710,00 € и 777,80 € — PDF BMWSB «Beispiele für die Berechnung des Wohngelds»,
  Stand 1. Januar 2025, Rechenbeispiel 7 (фрагмент `BMWSB_2025_BSP7` канона);
* 463 € на 31.12.2024 — арифметика текста: Anlagen 2, 3 BGBl. I 2022 S. 2160, Anlage 1 1. WoGFV,
  шаги Anlage 3 (независимая программа `corpus/laws/de/wohngeld/tools/reference_calc.py`: z4 = 463,2504131300);
* REQUIRES_JUDGMENT — § 21 Nr. 3 WoGG («soweit die Inanspruchnahme missbräuchlich wäre»);
* исключение — § 7 Abs. 1 S. 1 Nr. 1 и § 21 Nr. 2 WoGG.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[5]
sys.path.insert(0, str(ROOT / "engines" / "lawref"))

from lawref.base.canon import canonical_bytes  # noqa: E402
from lawref.case.cases import check_registration  # noqa: E402
from lawref.evaluator import EvaluationRequest, evaluate  # noqa: E402

W = "urn:de:social:clir:wohngeld#"
P = "urn:de:social:clir:wohngeld:param:"

# (дело, вопрос) → (статус вычисления, статус истинности, решающее правило, его якорь,
#                   выбранная строка параметра и её якорь — или None)
EXPECTED = {
    ("Familie2025", "einkommen-1710"): ("COMPUTED", "TRUE_ONLY", W + "MonatlichesGesamteinkommen", W + "WOGG_13_ABS2_ED2025", None),
    ("Familie2025", "miete-777-80"): ("COMPUTED", "TRUE_ONLY", W + "ZuBeruecksichtigendeMiete", W + "WOGG_11_ABS1_ED2025", None),
    ("Familie2025", "wohngeld-485"): ("COMPUTED", "TRUE_ONLY", W + "WohngeldGerundetBisZwoelf", W + "WOGG_19_ABS2_ED2025",
                                      (P + "WertBMitglieder4#2025-01-01", W + "ZWEITE_WOGFV_ANLAGEN_1_3")),
    ("Familie2025", "wohngeld-463"): ("COMPUTED", "NEITHER", None, None, None),
    ("Familie2025", "anspruch-485"): ("COMPUTED", "TRUE_ONLY", W + "Wohngeldanspruch", W + "WOGG_21_ED2025", None),
    ("Familie20241231", "wohngeld-463"): ("COMPUTED", "TRUE_ONLY", W + "WohngeldGerundetBisZwoelf", W + "WOGG_19_ABS2_ED2023",
                                          (P + "WertBMitglieder4#2023-01-01", W + "WPG_ANLAGEN_2_3")),
    ("Familie20241231", "wohngeld-485"): ("COMPUTED", "NEITHER", None, None, None),
    ("FamilieOhneWuerdigung", "wohngeld-485"): ("COMPUTED", "TRUE_ONLY", W + "WohngeldGerundetBisZwoelf", W + "WOGG_19_ABS2_ED2025", None),
    ("FamilieOhneWuerdigung", "anspruch-485"): ("REQUIRES_JUDGMENT", "NEITHER", None, None, None),
    ("AlleinGrundsicherung", "kein-anspruch-alle-ausgeschlossen"):
        ("COMPUTED", "TRUE_ONLY", W + "AlleHaushaltsmitgliederAusgeschlossen", W + "WOGG_21_ED2025", None),
    ("AlleinGrundsicherung", "wohngeld-485"): ("COMPUTED", "NEITHER", None, None, None),
}


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"{' '.join(command)}\n{completed.stderr}\n{completed.stdout}")
    return json.loads(completed.stdout)


def selected_rows(result: dict) -> set[str]:
    rows = set()
    for node in result["proofGraph"]["nodes"]:
        for selection in (node.get("attributes") or {}).get("a3Selections") or []:
            rows.add(selection.get("row"))
    return rows


def check(law: str, output: Path) -> None:
    entries = {entry.name for entry in check_registration(PACKAGE)}
    if entries != {case for case, _ in EXPECTED}:
        raise RuntimeError(f"Состав зарегистрированных дел расходится с проверкой: {sorted(entries)}")
    if check_registration(PACKAGE.parents[1]):
        raise RuntimeError("Дела примера ошибочно отнесены к родительскому канону")
    for (case, query), (evaluation, status, rule, anchor, row) in EXPECTED.items():
        saved = output / case / query
        command = [law, "ask", str(PACKAGE), "--case", case,
                   "--query-json", str(PACKAGE / "queries" / f"{query}.json"), "--out", str(saved)]
        result = run_json(command)
        answer, = result["results"]
        if (answer["evaluationStatus"], answer["truthStatus"]) != (evaluation, status):
            raise RuntimeError(f"{case}/{query}: ожидалось {evaluation}/{status}, получено "
                               f"{answer['evaluationStatus']}/{answer['truthStatus']}")
        requests = [item["predicate"] for item in answer.get("judgmentRequests") or []]
        if evaluation == "REQUIRES_JUDGMENT":
            if requests != [W + "missbraeuchliche_inanspruchnahme"]:
                raise RuntimeError(f"{case}/{query}: запрос суждения {requests}")
        elif requests:
            raise RuntimeError(f"{case}/{query}: лишние запросы суждения {requests}")
        request = json.loads((saved / "request.json").read_bytes())
        nodes = {node["id"]: node for node in request["ir"]["nodes"]}
        if rule is not None:
            applied = any(f":apply:{rule}:" in node["id"] or node.get("rule") == rule
                          for node in result["proofGraph"]["nodes"])
            grounded = anchor in (nodes.get(rule, {}).get("anchors") or []) and anchor in nodes
            if not applied or not grounded:
                raise RuntimeError(f"{case}/{query}: нет применения {rule} с якорем {anchor}")
        if row is not None:
            row_id, row_anchor = row
            if row_id not in selected_rows(result):
                raise RuntimeError(f"{case}/{query}: не выбрана строка параметра {row_id}")
            anchored = any(row_id.split("#")[1] in node_id and row_id.split("#")[0].rsplit(":", 1)[1] in node_id
                           and row_anchor in (node.get("anchors") or []) for node_id, node in nodes.items())
            if not anchored or row_anchor not in nodes:
                raise RuntimeError(f"{case}/{query}: строка {row_id} без якоря {row_anchor}")
        oracle = evaluate(EvaluationRequest.from_dict(request))
        replay = run_json([law, "eval", str(saved)])
        again = run_json(command[:-1] + [str(saved) + "-again"])
        expected_bytes = canonical_bytes(result)
        if canonical_bytes(oracle) != expected_bytes:
            raise RuntimeError(f"{case}/{query}: Rust != Python")
        if canonical_bytes(replay) != expected_bytes:
            raise RuntimeError(f"{case}/{query}: ask != replay")
        if canonical_bytes(again) != expected_bytes:
            raise RuntimeError(f"{case}/{query}: повторный ask дал другие байты")
        print(f"{case}/{query}: {evaluation}/{status}; основание, редакция, Rust/Python, replay, повтор — OK", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--law", default=str(ROOT / "law"), help="пользовательский бинарь law или launcher checkout")
    parser.add_argument("--out", type=Path, help="сохранить request/result/ask; по умолчанию временный каталог")
    args = parser.parse_args()
    try:
        if args.out:
            check(args.law, args.out.resolve())
        else:
            with tempfile.TemporaryDirectory(prefix="wohngeld-examples-") as temporary:
                check(args.law, Path(temporary))
    except (RuntimeError, ValueError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"wohngeld examples: 4 дела, {len(EXPECTED)} вопросов — OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
