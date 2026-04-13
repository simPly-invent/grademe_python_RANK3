#!/usr/bin/env python3
"""
examshell.py — Clone d'examshell pour les exercices Python rank 03.
Commandes : start, status, grademe, finish, help
"""

import argparse
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from grader import run_tests
from display import (
    print_banner,
    print_subject,
    print_status,
    print_result,
    print_error,
    print_success,
    print_info,
)

BASE_DIR    = Path(__file__).parent
SUBJECTS_FILE = BASE_DIR / "subjects" / "rank03.json"
SESSIONS_DIR  = BASE_DIR / "sessions"
RENDU_DIR     = BASE_DIR / "rendu"
SESSION_FILE  = SESSIONS_DIR / "current.json"

EXAM_DURATION = 3600  # 1 heure en s


# ─── Session helpers ──────────────────────────────────────────────────────────

def load_subjects() -> list[dict]:
    with open(SUBJECTS_FILE) as f:
        data = json.load(f)
    return data["subjects"]


def load_session() -> dict | None:
    if not SESSION_FILE.exists():
        return None
    with open(SESSION_FILE) as f:
        return json.load(f)


def save_session(session: dict) -> None:
    SESSIONS_DIR.mkdir(exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)


def delete_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def elapsed_str(start_ts: float) -> str:
    elapsed = int(time.time() - start_ts)
    return f"{elapsed // 60:02d}:{elapsed % 60:02d}"


def remaining_str(start_ts: float) -> str:
    remaining = max(0, EXAM_DURATION - int(time.time() - start_ts))
    return f"{remaining // 60:02d}:{remaining % 60:02d}"


def is_expired(session: dict) -> bool:
    return time.time() - session["started_at"] > EXAM_DURATION


# ─── Commandes ────────────────────────────────────────────────────────────────

def cmd_start(args) -> None:
    """Démarre une nouvelle session d'examen."""
    session = load_session()
    if session:
        print_error("Une session est déjà en cours. Fais 'finish' pour la terminer d'abord.")
        return

    subjects = load_subjects()

    # Filtre optionnel par difficulté
    difficulty = getattr(args, "difficulty", None)
    if difficulty:
        filtered = [s for s in subjects if s["difficulty"] == difficulty]
        if not filtered:
            print_error(f"Aucun sujet de difficulté '{difficulty}'.")
            return
        subjects = filtered

    subject = random.choice(subjects)

    # Prépare le dossier rendu/
    RENDU_DIR.mkdir(exist_ok=True)
    # Vide le dossier rendu/ des anciens fichiers
    for f in RENDU_DIR.glob("*.py"):
        f.unlink()

    # Crée le fichier de départ avec la signature
    student_file = RENDU_DIR / f"{subject['id']}.py"
    student_file.write_text(
        f"# {subject['title']}\n"
        f"# Rank 03 — Python\n\n"
        f"{subject['signature']}\n"
        f"    pass\n"
    )

    session = {
        "subject_id": subject["id"],
        "started_at": time.time(),
        "attempts":   0,
        "best_score": 0,
    }
    save_session(session)

    print_banner()
    print_subject(subject)
    print_success(f"\nFichier créé : rendu/{subject['id']}.py")
    print_info("Commandes : status · grademe · finish")


def cmd_status(args) -> None:
    """Affiche le sujet en cours et le temps restant."""
    session = load_session()
    if not session:
        print_error("Pas de session en cours. Lance 'start' pour commencer.")
        return

    subjects = {s["id"]: s for s in load_subjects()}
    subject  = subjects[session["subject_id"]]

    if is_expired(session):
        print_error("Temps écoulé ! Lance 'finish' pour terminer.")
        return

    print_subject(subject)
    print_status(
        elapsed=elapsed_str(session["started_at"]),
        remaining=remaining_str(session["started_at"]),
        attempts=session["attempts"],
        best_score=session["best_score"],
    )


def cmd_grademe(args) -> None:
    """Corrige le fichier dans rendu/ et affiche le score."""
    session = load_session()
    if not session:
        print_error("Pas de session en cours. Lance 'start' pour commencer.")
        return

    if is_expired(session):
        print_error("Temps écoulé ! La session est terminée.")
        cmd_finish(args)
        return

    subjects = {s["id"]: s for s in load_subjects()}
    subject  = subjects[session["subject_id"]]

    student_file = RENDU_DIR / f"{subject['id']}.py"
    if not student_file.exists():
        print_error(f"Fichier introuvable : rendu/{subject['id']}.py")
        return

    session["attempts"] += 1

    print_info(f"Correction en cours… (tentative #{session['attempts']})")
    results, score = run_tests(subject, student_file)

    if score > session["best_score"]:
        session["best_score"] = score
    save_session(session)

    print_result(results, score)

    if score == 100:
        print_success("✓ 100% — Excellent ! Tu peux lancer 'finish'.")


def cmd_finish(args) -> None:
    """Termine la session et affiche le résumé."""
    session = load_session()
    if not session:
        print_error("Pas de session en cours.")
        return

    subjects = {s["id"]: s for s in load_subjects()}
    subject  = subjects[session["subject_id"]]

    duration = int(time.time() - session["started_at"])
    dur_str  = f"{duration // 60}m {duration % 60}s"

    print_banner()
    print(f"\n  Sujet    : {subject['title']}")
    print(f"  Durée    : {dur_str}")
    print(f"  Tentatives : {session['attempts']}")
    print(f"  Meilleur score : {session['best_score']}%")

    # Sauvegarde historique
    history_file = SESSIONS_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    history_data = {
        **session,
        "subject_title": subject["title"],
        "finished_at":   time.time(),
        "duration_sec":  duration,
    }
    SESSIONS_DIR.mkdir(exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(history_data, f, indent=2)

    delete_session()
    print_info(f"\nSession sauvegardée → sessions/{history_file.name}")
    print()


def cmd_help(args) -> None:
    print_banner()
    print("""
  Commandes disponibles :

    start [-d easy|medium|hard]   Démarre un examen (sujet aléatoire)
    status                        Affiche le sujet et le temps restant
    grademe                       Corrige ton fichier dans rendu/
    finish                        Termine la session et affiche le bilan
    help                          Affiche ce message
""")


# ─── Point d'entrée ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="examshell",
        description="Clone d'examshell — Rank 03 Python",
        add_help=False,
    )
    subparsers = parser.add_subparsers(dest="command")

    p_start = subparsers.add_parser("start")
    p_start.add_argument("-d", "--difficulty", choices=["easy", "medium", "hard"])
    p_start.set_defaults(func=cmd_start)

    p_status = subparsers.add_parser("status")
    p_status.set_defaults(func=cmd_status)

    p_grade = subparsers.add_parser("grademe")
    p_grade.set_defaults(func=cmd_grademe)

    p_finish = subparsers.add_parser("finish")
    p_finish.set_defaults(func=cmd_finish)

    p_help = subparsers.add_parser("help")
    p_help.set_defaults(func=cmd_help)

    args = parser.parse_args()

    if not args.command:
        cmd_help(args)
        return

    args.func(args)


if __name__ == "__main__":
    main()
