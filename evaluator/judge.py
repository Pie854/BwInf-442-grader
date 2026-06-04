#!/usr/bin/env python3
"""
BwInf Grader – judge.py
=======================
Aufruf:
    python evaluator/judge.py
        --submission-dir submission/
        --instances-dir  data/instances/
        --leaderboard    data/leaderboard.json
        --submitter      <github-username>
        --result-file    result.json

.out-Dateiformat (pro Testfall):
    Zeile 1:  Kosten als Integer (niedriger = besser)
    Zeile 2+: Beweis / Lösung (wird an check_solution() übergeben)

Punkteformel pro Testfall:
    points = (beste_bekannte_kosten / eigene_kosten) * 100
    → eigene_kosten == beste → 100 Punkte
    → eigene_kosten schlechter → weniger Punkte
    → eigene_kosten besser als bisher beste → >100 Punkte möglich
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# ✏️  HIER: Checker implementieren
# ---------------------------------------------------------------------------

def check_solution(instance_text: str, cost: int, proof_lines: list[str]) -> bool:
    """
    Prüft ob die eingereichte Lösung gültig ist.

    Args:
        instance_text:  Inhalt der Eingabedatei (data/instances/<id>.txt)
        cost:           Angegebene Kosten (erste Zeile der .out-Datei)
        proof_lines:    Restliche Zeilen der .out-Datei als Liste

    Returns:
        True  → Lösung ist gültig
        False → Lösung ist ungültig (gibt 0 Punkte)
    """
    # TODO: Checker hier implementieren
    # Beispiel (immer akzeptieren, solange cost > 0):
    return cost > 0


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

NUM_TESTCASES = 10


def load_leaderboard(path: str) -> dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    # Leeres Leaderboard initialisieren
    return {
        "best_costs": {str(i): None for i in range(1, NUM_TESTCASES + 1)},
        "rankings": []
    }


def save_leaderboard(path: str, lb: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lb, f, indent=2, ensure_ascii=False)


def parse_output_file(path: str) -> tuple[int, list[str]]:
    """Liest eine .out-Datei und gibt (kosten, proof_lines) zurück."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines:
        raise ValueError("Datei ist leer.")
    cost = int(lines[0].strip())
    proof_lines = lines[1:]
    return cost, proof_lines


def compute_points(own_cost: int, best_cost: int) -> float:
    """Berechnet Punkte: (best / own) * 100. Niedriger = besser."""
    if own_cost <= 0:
        raise ValueError("Kosten müssen > 0 sein.")
    return (best_cost / own_cost) * 100.0


# ---------------------------------------------------------------------------
# Hauptlogik
# ---------------------------------------------------------------------------

def run(submission_dir: str, instances_dir: str, leaderboard_path: str,
        submitter: str, result_file: str) -> None:

    lb = load_leaderboard(leaderboard_path)
    testcases = []
    errors = []

    for tc_id in range(1, NUM_TESTCASES + 1):
        tc_str = str(tc_id)
        out_path = os.path.join(submission_dir, f"{tc_id}.out")
        inst_path = os.path.join(instances_dir, f"{tc_id}.txt")

        entry = {"id": tc_id, "valid": False, "cost": None,
                 "best_cost": lb["best_costs"].get(tc_str), "points": 0.0}

        if not os.path.exists(out_path):
            entry["error"] = "Datei fehlt"
            testcases.append(entry)
            continue

        if not os.path.exists(inst_path):
            entry["error"] = "Instanz nicht gefunden (Serverfehler)"
            testcases.append(entry)
            continue

        try:
            cost, proof_lines = parse_output_file(out_path)
            entry["cost"] = cost
        except Exception as e:
            entry["error"] = f"Parse-Fehler: {e}"
            testcases.append(entry)
            continue

        instance_text = open(inst_path, encoding="utf-8").read()

        try:
            valid = check_solution(instance_text, cost, proof_lines)
        except Exception as e:
            entry["error"] = f"Checker-Ausnahme: {e}"
            testcases.append(entry)
            continue

        if not valid:
            entry["error"] = "Checker: Lösung ungültig"
            testcases.append(entry)
            continue

        entry["valid"] = True

        # Beste bekannte Kosten aktualisieren
        current_best = lb["best_costs"].get(tc_str)
        if current_best is None or cost < current_best:
            lb["best_costs"][tc_str] = cost
            entry["best_cost"] = cost  # wird für Punkteberechnung unten genutzt

        # Punkte berechnen (basierend auf dem best_cost *nach* diesem Update)
        best_for_scoring = lb["best_costs"][tc_str]
        entry["best_cost"] = best_for_scoring
        entry["points"] = compute_points(cost, best_for_scoring)

        testcases.append(entry)

    # Gesamtpunktzahl
    total_score = sum(tc["points"] for tc in testcases if tc["valid"])
    max_score = NUM_TESTCASES * 100

    # Leaderboard-Eintrag aktualisieren (bester Score bleibt stehen)
    rankings = lb.get("rankings", [])
    existing = next((r for r in rankings if r["user"] == submitter), None)

    timestamp = datetime.now(timezone.utc).isoformat()
    new_entry = {
        "user": submitter,
        "score": round(total_score, 4),
        "scores_per_tc": {str(tc["id"]): round(tc["points"], 4) for tc in testcases},
        "costs_per_tc": {str(tc["id"]): tc["cost"] for tc in testcases if tc["valid"]},
        "timestamp": timestamp,
    }

    if existing is None:
        rankings.append(new_entry)
    elif total_score > existing["score"]:
        rankings[rankings.index(existing)] = new_entry
    # sonst: alter Score war besser → nicht überschreiben

    lb["rankings"] = sorted(rankings, key=lambda r: r["score"], reverse=True)
    save_leaderboard(leaderboard_path, lb)

    result = {
        "status": "ok",
        "submitter": submitter,
        "total_score": round(total_score, 4),
        "max_score": max_score,
        "testcases": testcases,
        "timestamp": timestamp,
    }
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Fertig. Score: {total_score:.2f}/{max_score}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission-dir", required=True)
    parser.add_argument("--instances-dir",  required=True)
    parser.add_argument("--leaderboard",    required=True)
    parser.add_argument("--submitter",      required=True)
    parser.add_argument("--result-file",    required=True)
    args = parser.parse_args()

    try:
        run(
            submission_dir=args.submission_dir,
            instances_dir=args.instances_dir,
            leaderboard_path=args.leaderboard,
            submitter=args.submitter,
            result_file=args.result_file,
        )
    except Exception as e:
        # Unerwarteter Fehler → result.json mit Fehlermeldung schreiben
        with open(args.result_file, "w", encoding="utf-8") as f:
            json.dump({"status": "error", "error": str(e)}, f)
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)