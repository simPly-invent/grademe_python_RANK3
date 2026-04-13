#!/usr/bin/env python3
"""
menu.py — Interface terminal interactive (TUI).
Lancé via `make` ou `make menu`.
Navigation au clavier, mode examen, historique.
"""

import json
import os
import sys
import time
import termios
import tty
from pathlib import Path

BASE_DIR      = Path(__file__).parent
SUBJECTS_FILE = BASE_DIR / "subjects" / "rank03.json"
SESSIONS_DIR  = BASE_DIR / "sessions"


R     = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
RED   = "\033[31m"
GREEN = "\033[32m"
YEL   = "\033[33m"
BLUE  = "\033[34m"
CYAN  = "\033[36m"
WHITE = "\033[37m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR       = "\033[2J\033[H"

def c(color, text): return f"{color}{text}{R}"
def move(row, col): return f"\033[{row};{col}H"
def clear_line():   return "\033[2K"



def getch() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\033":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                return {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT"}.get(ch3, "")
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)



def load_subjects() -> list[dict]:
    with open(SUBJECTS_FILE) as f:
        return json.load(f)["subjects"]


def load_history() -> list[dict]:
    sessions = []
    if not SESSIONS_DIR.exists():
        return []
    for f in sorted(SESSIONS_DIR.glob("session_*.json"), reverse=True)[:10]:
        with open(f) as fh:
            sessions.append(json.load(fh))
    return sessions


def get_terminal_size() -> tuple[int, int]:
    size = os.get_terminal_size()
    return size.lines, size.columns


DIFF_COLOR = {"easy": GREEN, "medium": YEL, "hard": RED}
DIFF_LABEL = {"easy": "EASY", "medium": "MED ", "hard": "HARD"}


def draw_header(title: str = "examshell · Rank 03 Python") -> None:
    rows, cols = get_terminal_size()
    bar = "─" * (cols - 2)
    print(c(CYAN + BOLD, f"┌{bar}┐"))
    padding = (cols - 2 - len(title)) // 2
    print(c(CYAN + BOLD, "│") + " " * padding + c(BOLD, title) + " " * (cols - 2 - padding - len(title)) + c(CYAN + BOLD, "│"))
    print(c(CYAN + BOLD, f"└{bar}┘"))


def draw_footer(hints: str) -> None:
    rows, cols = get_terminal_size()
    bar = "─" * (cols - 2)
    print(c(DIM, f"┌{bar}┐"))
    padded = hints[:cols-4]
    print(c(DIM, "│ ") + padded + " " * (cols - 4 - len(padded)) + c(DIM, " │"))
    print(c(DIM, f"└{bar}┘"))


def draw_menu(title: str, items: list[str], selected: int,
              prefix_fn=None, suffix_fn=None) -> None:
    print()
    print(f"  {c(DIM, title)}")
    print()
    for i, item in enumerate(items):
        prefix = prefix_fn(i) if prefix_fn else "  "
        suffix = suffix_fn(i) if suffix_fn else ""
        if i == selected:
            print(f"  {c(CYAN + BOLD, '▶')} {c(BOLD, item)}{suffix}")
        else:
            print(f"    {c(DIM, item)}{suffix}")
    print()


def screen_main() -> str:
    """Menu principal. Retourne la section choisie."""
    items = [
        "  Commencer un examen",
        "  Mode entraînement  (sujet au choix)",
        "  Mode challenge     (tous les sujets, easy → hard)",
        "  Historique         (sessions passées)",
        "  Quitter",
    ]
    sel = 0
    while True:
        print(HIDE_CURSOR + CLEAR, end="")
        draw_header()
        draw_menu("Que veux-tu faire ?", items, sel)
        draw_footer("↑ ↓ naviguer   Entrée sélectionner   q quitter")

        key = getch()
        if key in ("UP",   "k") and sel > 0:            sel -= 1
        elif key in ("DOWN","j") and sel < len(items)-1: sel += 1
        elif key in ("\r", "\n"):
            return ["exam", "training", "challenge", "history", "quit"][sel]
        elif key in ("q", "Q"):
            return "quit"


def screen_difficulty() -> str | None:
    """Sélection de difficulté. Retourne 'easy'|'medium'|'hard'|None."""
    items = ["  Facile  (easy)", "  Moyen   (medium)", "  Difficile (hard)", "  Aléatoire (tous)"]
    values = ["easy", "medium", "hard", None]
    sel = 3
    while True:
        print(HIDE_CURSOR + CLEAR, end="")
        draw_header("Choisir la difficulté")
        draw_menu("Difficulté du sujet :", items, sel)
        draw_footer("↑ ↓ naviguer   Entrée valider   Echap retour")

        key = getch()
        if key in ("UP",   "k") and sel > 0:            sel -= 1
        elif key in ("DOWN","j") and sel < len(items)-1: sel += 1
        elif key in ("\r", "\n"):
            return values[sel]
        elif key == "\033":
            return "back"


def screen_subject_picker(subjects: list[dict]) -> dict | None:
    """Sélection d'un sujet spécifique. Retourne le sujet ou None."""
    order = {"easy": 0, "medium": 1, "hard": 2}
    sorted_subjects = sorted(subjects, key=lambda s: (order[s["difficulty"]], s["title"]))

    items = [s["title"] for s in sorted_subjects]
    sel   = 0

    while True:
        print(HIDE_CURSOR + CLEAR, end="")
        draw_header("Choisir un sujet")

        def suffix(i):
            d = sorted_subjects[i]["difficulty"]
            return f"  {c(DIFF_COLOR[d], '[' + DIFF_LABEL[d] + ']')}"

        draw_menu("Sélectionne un exercice :", items, sel, suffix_fn=suffix)
        draw_footer("↑ ↓ naviguer   Entrée sélectionner   Echap retour")

        key = getch()
        if key in ("UP",   "k") and sel > 0:            sel -= 1
        elif key in ("DOWN","j") and sel < len(items)-1: sel += 1
        elif key in ("\r", "\n"):
            return sorted_subjects[sel]
        elif key == "\033":
            return None


def screen_subject_preview(subject: dict, mode: str = "exam") -> str:
    """Affiche le sujet et demande confirmation. Retourne 'start'|'back'."""
    while True:
        print(HIDE_CURSOR + CLEAR, end="")
        draw_header(f"Sujet : {subject['title']}")

        d = subject["difficulty"]
        print()
        print(f"  Difficulté : {c(DIFF_COLOR[d] + BOLD, DIFF_LABEL[d])}")
        print()
        print(f"  {c(DIM, 'ASSIGNMENT')}")
        words  = subject["assignment"].split()
        line   = "  "
        for word in words:
            if len(line) + len(word) + 1 > 74:
                print(line)
                line = "    " + word
            else:
                line += (" " if line != "  " else "") + word
        if line.strip(): print(line)
        print()
        print(f"  {c(DIM, 'SIGNATURE')}")
        print(f"  {c(CYAN, subject['signature'])}")
        print()
        print(f"  {c(DIM, 'EXEMPLES')}")
        for test in subject["tests"][:2]:
            args = test["input"][0]
            exp  = test["expected"]
            print(f"    {c(DIM, str(args))}  →  {c(GREEN, str(exp))}")
        print()

        items = ["  Lancer l'examen", "  Retour"]
        sel   = 0
        pos = [0, 1]
        sel = 0

        for i, it in enumerate(items):
            if i == sel:
                print(f"  {c(CYAN + BOLD, '▶')} {c(BOLD, it)}")
            else:
                print(f"    {c(DIM, it)}")
        print()
        draw_footer("↑ ↓ naviguer   Entrée valider")

        key = getch()
        if key in ("UP", "k"):
            sel = max(0, sel - 1)
        elif key in ("DOWN", "j"):
            sel = min(1, sel + 1)
        elif key in ("\r", "\n"):
            return "start" if sel == 0 else "back"
        elif key == "\033":
            return "back"



def screen_exam_running(subject: dict) -> None:
    """Lance examshell pour ce sujet et attend que l'utilisateur revienne."""
    import subprocess
    examshell = BASE_DIR / "examshell.py"


    session_file = SESSIONS_DIR / "current.json"
    if session_file.exists():
        session_file.unlink()

    rendu_dir = BASE_DIR / "rendu"
    rendu_dir.mkdir(exist_ok=True)
    for f in rendu_dir.glob("*.py"):
        f.unlink()
    student_file = rendu_dir / f"{subject['id']}.py"
    student_file.write_text(
        f"# {subject['title']}\n# Rank 03 — Python\n\n{subject['signature']}\n    pass\n"
    )

    SESSIONS_DIR.mkdir(exist_ok=True)
    session = {
        "subject_id": subject["id"],
        "started_at": time.time(),
        "attempts":   0,
        "best_score": 0,
    }
    with open(session_file, "w") as f:
        json.dump(session, f)

    print(SHOW_CURSOR + CLEAR, end="")
    draw_header(f"Examen en cours : {subject['title']}")
    print()
    sid = subject['id']
    print(f"  Fichier à éditer : {c(CYAN + BOLD, f'rendu/{sid}.py')}")
    print()
    print(f"  Commandes disponibles :")
    print(f"    {c(CYAN, 'python3 examshell.py grademe')}  ← corriger ton code")
    print(f"    {c(CYAN, 'python3 examshell.py status')}   ← voir le sujet + chrono")
    print(f"    {c(CYAN, 'python3 examshell.py finish')}   ← terminer la session")
    print()
    print(f"  {c(DIM, 'Ouvre un autre terminal et édite ton fichier.')}")
    print(f"  {c(DIM, 'Reviens ici et appuie sur Entrée quand tu as terminé.')}")
    print()
    print(f"  {c(YEL, '→')} Appuie sur {c(BOLD, 'Entrée')} pour revenir au menu (ou {c(BOLD, 'g')} pour grademe direct).")
    print()

    key = getch()
    if key in ("g", "G"):
        print(SHOW_CURSOR)
        subprocess.run([sys.executable, str(examshell), "grademe"])
        print()
        input(c(DIM, "  Appuie sur Entrée pour continuer…"))


def screen_challenge(subjects: list[dict]) -> None:
    """
    Mode challenge : tous les sujets dans l'ordre easy → medium → hard.
    L'utilisateur doit obtenir 100% sur chaque pour passer au suivant.
    """
    from grader import run_tests

    order = {"easy": 0, "medium": 1, "hard": 2}
    sorted_subjects = sorted(subjects, key=lambda s: (order[s["difficulty"]], s["title"]))

    rendu_dir = BASE_DIR / "rendu"
    rendu_dir.mkdir(exist_ok=True)

    total    = len(sorted_subjects)
    results  = []

    print(SHOW_CURSOR + CLEAR, end="")
    draw_header("Mode Challenge — tous les sujets")
    print()
    print(f"  {total} sujets à résoudre, du plus facile au plus difficile.")
    print(f"  Pour chaque sujet :")
    print(f"    1. Édite {c(CYAN, 'rendu/<sujet>.py')} dans ton éditeur")
    print(f"    2. Reviens ici et appuie sur {c(BOLD, 'g')} pour corriger")
    print(f"    3. Obtiens {c(GREEN, '100%')} pour passer au suivant")
    print()
    print(f"  Appuie sur {c(BOLD, 'Entrée')} pour commencer…")
    getch()

    for idx, subject in enumerate(sorted_subjects):
        d         = subject["difficulty"]
        attempts  = 0
        score     = 0
        start_ts  = time.time()

        for f in rendu_dir.glob("*.py"):
            f.unlink()
        student_file = rendu_dir / f"{subject['id']}.py"
        student_file.write_text(
            f"# {subject['title']}\n# Rank 03 — Python\n\n{subject['signature']}\n    pass\n"
        )

        while score < 100:
            print(SHOW_CURSOR + CLEAR, end="")
            draw_header(f"Challenge {idx+1}/{total} : {subject['title']}")

            # Barre de progression globale
            filled = int(20 * idx / total)
            bar = c(GREEN, "█" * filled) + c(DIM, "░" * (20 - filled))
            print(f"\n  Progression : [{bar}] {idx}/{total}")
            print()
            print(f"  Difficulté : {c(DIFF_COLOR[d] + BOLD, DIFF_LABEL[d])}")
            print()
            print(f"  {c(DIM, 'ASSIGNMENT')}")
            words = subject["assignment"].split()
            line  = "  "
            for word in words:
                if len(line) + len(word) + 1 > 74:
                    print(line); line = "    " + word
                else:
                    line += (" " if line != "  " else "") + word
            if line.strip(): print(line)
            print()
            print(f"  {c(CYAN, subject['signature'])}")
            print()
            csid = subject['id']
            print(f"  Fichier : {c(CYAN + BOLD, f'rendu/{csid}.py')}")
            print(f"  Tentatives : {attempts}   Score : {c(GREEN if score==100 else YEL, str(score)+'%')}")
            print()
            print(f"  {c(BOLD, 'g')} → corriger   {c(BOLD, 's')} → voir les tests   {c(BOLD, 'q')} → abandonner")
            print()

            key = getch()

            if key in ("g", "G"):
                test_results, score = run_tests(subject, student_file)
                attempts += 1
                print(CLEAR, end="")
                draw_header(f"Résultats : {subject['title']}")
                print()
                for r in test_results:
                    i = r["index"] + 1
                    n = len(test_results)
                    if r["error"]:
                        print(f"  {c(RED, '✗')} Test {i}/{n}  {c(RED, r['error'][:60])}")
                    elif r["passed"]:
                        print(f"  {c(GREEN, '✓')} Test {i}/{n}")
                    else:
                        print(f"  {c(RED, '✗')} Test {i}/{n}  attendu={c(GREEN, str(r['expected']))}  obtenu={c(RED, str(r['actual']))}")
                print()
                blen   = 30
                filled = int(blen * score / 100)
                bc     = GREEN if score == 100 else (YEL if score >= 50 else RED)
                bar    = c(bc, "█" * filled) + c(DIM, "░" * (blen - filled))
                print(f"  Score : [{bar}] {c(BOLD + bc, str(score)+'%')}")
                print()
                if score == 100:
                    print(f"  {c(GREEN + BOLD, '✓ Parfait ! Sujet suivant dans 2s…')}")
                    time.sleep(2)
                else:
                    print(f"  Appuie sur une touche pour continuer…")
                    getch()

            elif key in ("s", "S"):
                print(CLEAR, end="")
                draw_header(f"Tests : {subject['title']}")
                print()
                for i, test in enumerate(subject["tests"]):
                    args = test["input"][0]
                    exp  = test["expected"]
                    print(f"  Test {i+1} : {c(DIM, str(args))}  →  {c(GREEN, str(exp))}")
                print()
                print("  Appuie sur une touche pour revenir…")
                getch()

            elif key in ("q", "Q"):
                results.append({
                    "title": subject["title"],
                    "score": score,
                    "attempts": attempts,
                    "duration": int(time.time() - start_ts),
                    "abandoned": True,
                })
                screen_challenge_results(results, sorted_subjects)
                return

        results.append({
            "title": subject["title"],
            "score": score,
            "attempts": attempts,
            "duration": int(time.time() - start_ts),
            "abandoned": False,
        })

    screen_challenge_results(results, sorted_subjects)


def screen_challenge_results(results: list[dict], subjects: list[dict]) -> None:
    """Bilan final du mode challenge."""
    print(SHOW_CURSOR + CLEAR, end="")
    draw_header("Bilan du mode Challenge")
    print()

    total_done = sum(1 for r in results if not r.get("abandoned"))
    total      = len(subjects)
    total_time = sum(r["duration"] for r in results)

    for r in results:
        icon = c(GREEN, "✓") if r["score"] == 100 else c(RED, "✗")
        dur  = f"{r['duration']//60}m{r['duration']%60:02d}s"
        print(f"  {icon} {r['title']:<28} {c(GREEN if r['score']==100 else RED, str(r['score'])+'%'):>6}  {r['attempts']} essai(s)  {dur}")

    print()
    pct = int(100 * total_done / total)
    bar = c(GREEN, "█" * int(30 * pct / 100)) + c(DIM, "░" * (30 - int(30 * pct / 100)))
    print(f"  [{bar}] {total_done}/{total} sujets réussis")
    print(f"  Temps total : {total_time//60}m {total_time%60:02d}s")
    print()
    print(f"  Appuie sur une touche pour revenir au menu…")
    getch()


def screen_history() -> None:
    """Affiche l'historique des sessions."""
    sessions = load_history()
    print(HIDE_CURSOR + CLEAR, end="")
    draw_header("Historique des sessions")
    print()

    if not sessions:
        print(f"  {c(DIM, 'Aucune session enregistrée.')}")
    else:
        print(f"  {'Sujet':<30} {'Score':>6}  {'Durée':>8}  {'Essais':>6}")
        print(f"  {c(DIM, '─' * 58)}")
        for s in sessions:
            title = s.get("subject_title", s.get("subject_id", "?"))[:28]
            score = s.get("best_score", 0)
            dur   = s.get("duration_sec", 0)
            att   = s.get("attempts", 0)
            sc    = c(GREEN if score == 100 else YEL, f"{score}%")
            print(f"  {title:<30} {sc:>6}  {dur//60}m{dur%60:02d}s  {att:>6}")

    print()
    draw_footer("Entrée ou q → retour")
    getch()


# ─── Boucle principale ────────────────────────────────────────────────────────

def main() -> None:
    subjects = load_subjects()

    try:
        while True:
            action = screen_main()

            if action == "quit":
                print(SHOW_CURSOR + CLEAR, end="")
                print(c(CYAN, "\n  À bientôt !\n"))
                break

            elif action == "exam":
                diff = screen_difficulty()
                if diff == "back":
                    continue
                pool = [s for s in subjects if diff is None or s["difficulty"] == diff]
                if not pool:
                    continue
                import random
                subject = random.choice(pool)
                res = screen_subject_preview(subject)
                if res == "start":
                    screen_exam_running(subject)

            elif action == "training":
                subject = screen_subject_picker(subjects)
                if subject is None:
                    continue
                res = screen_subject_preview(subject, mode="training")
                if res == "start":
                    screen_exam_running(subject)

            elif action == "challenge":
                screen_challenge(subjects)

            elif action == "history":
                screen_history()

    except KeyboardInterrupt:
        print(SHOW_CURSOR + CLEAR, end="")
        print(c(CYAN, "\n  À bientôt !\n"))


if __name__ == "__main__":
    main()