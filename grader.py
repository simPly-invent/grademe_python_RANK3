"""
grader.py — Correcteur automatique.
Exécute le fichier étudiant dans un subprocess isolé,
compare les sorties aux résultats attendus, retourne un score.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

TIMEOUT = 5  # secondes max par test


def _build_runner(subject: dict, student_file: Path) -> str:
    """
    Génère un script Python autonome qui :
    1. Importe la fonction de l'étudiant
    2. Exécute chaque test
    3. Affiche les résultats en JSON sur stdout
    """
    func_name = subject["signature"].split("(")[0].replace("def ", "").strip()
    tests_json = json.dumps(subject["tests"])

    return textwrap.dedent(f"""
import sys, json, traceback

# Charge le fichier étudiant
import importlib.util
spec = importlib.util.spec_from_file_location("student", {str(student_file)!r})
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

func = getattr(mod, {func_name!r}, None)
if func is None:
    print(json.dumps({{"error": "Fonction '{func_name}' introuvable"}}))
    sys.exit(1)

tests   = json.loads({tests_json!r})
results = []

for i, test in enumerate(tests):
    args     = test["input"][0] if len(test["input"]) == 1 else test["input"]
    expected = test["expected"]
    try:
        if isinstance(args, list) and not isinstance(args[0], list):
            # args est une liste plate de paramètres
            actual = func(*args)
        else:
            actual = func(*args)
        passed = (actual == expected)
        results.append({{
            "index":    i,
            "passed":   passed,
            "input":    args,
            "expected": expected,
            "actual":   actual,
            "error":    None,
        }})
    except Exception as e:
        results.append({{
            "index":    i,
            "passed":   False,
            "input":    args,
            "expected": expected,
            "actual":   None,
            "error":    str(e),
        }})

print(json.dumps(results))
""")


def run_tests(subject: dict, student_file: Path) -> tuple[list[dict], int]:
    """
    Lance les tests du sujet sur le fichier étudiant.
    Retourne (résultats, score_pourcentage).
    """
    runner_code = _build_runner(subject, student_file)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(runner_code)
        runner_path = tmp.name

    try:
        proc = subprocess.run(
            [sys.executable, runner_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return (
            [{"index": 0, "passed": False, "error": "Timeout dépassé", "input": None,
              "expected": None, "actual": None}],
            0,
        )
    finally:
        Path(runner_path).unlink(missing_ok=True)

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()

    if not stdout:
        error_msg = stderr or "Aucune sortie — erreur de syntaxe ?"
        return (
            [{"index": 0, "passed": False, "error": error_msg, "input": None,
              "expected": None, "actual": None}],
            0,
        )

    try:
        # Gère le cas où le runner retourne {"error": ...}
        parsed = json.loads(stdout)
        if isinstance(parsed, dict) and "error" in parsed:
            return (
                [{"index": 0, "passed": False, "error": parsed["error"],
                  "input": None, "expected": None, "actual": None}],
                0,
            )
        results = parsed
    except json.JSONDecodeError:
        return (
            [{"index": 0, "passed": False, "error": f"Sortie invalide : {stdout[:200]}",
              "input": None, "expected": None, "actual": None}],
            0,
        )

    passed = sum(1 for r in results if r["passed"])
    total  = len(results)
    score  = int(100 * passed / total) if total else 0

    return results, score
