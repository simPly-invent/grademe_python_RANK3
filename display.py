"""
display.py — Affichage coloré dans le terminal.
Utilise les codes ANSI natifs (pas de dépendance externe).
"""

# ─── Couleurs ANSI ────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

BLACK  = "\033[30m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
CYAN   = "\033[36m"
WHITE  = "\033[37m"

BG_GREEN = "\033[42m"
BG_RED   = "\033[41m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def print_banner() -> None:
    print()
    print(_c(BOLD + CYAN, "  ╔══════════════════════════════════════╗"))
    print(_c(BOLD + CYAN, "  ║       examshell  ·  Rank 03 Python   ║"))
    print(_c(BOLD + CYAN, "  ╚══════════════════════════════════════╝"))
    print()


def print_subject(subject: dict) -> None:
    diff_colors = {"easy": GREEN, "medium": YELLOW, "hard": RED}
    diff_color  = diff_colors.get(subject["difficulty"], WHITE)

    print()
    print(_c(BOLD, f"  ── {subject['title']} ") + _c(diff_color, f"[{subject['difficulty']}]"))
    print()
    print(_c(DIM, "  ASSIGNMENT"))
    # Wrap long lines
    words = subject["assignment"].split()
    line  = "  "
    for word in words:
        if len(line) + len(word) + 1 > 72:
            print(line)
            line = "    " + word
        else:
            line += (" " if line.strip() else "") + word
    if line.strip():
        print(line)
    print()
    print(_c(DIM, "  SIGNATURE"))
    print(f"  {_c(CYAN, subject['signature'])}")
    print()


def print_status(elapsed: str, remaining: str, attempts: int, best_score: int) -> None:
    print(_c(DIM, "  ─────────────────────────────────"))
    print(f"  Temps écoulé  : {_c(YELLOW, elapsed)}")
    print(f"  Temps restant : {_c(GREEN if remaining > '15:00' else RED, remaining)}")
    print(f"  Tentatives    : {attempts}")
    print(f"  Meilleur score: {_c(GREEN if best_score == 100 else YELLOW, str(best_score) + '%')}")
    print()


def print_result(results: list[dict], score: int) -> None:
    print()
    total  = len(results)
    passed = sum(1 for r in results if r["passed"])

    for r in results:
        idx  = r["index"] + 1
        if r["error"]:
            icon = _c(RED, "✗")
            msg  = _c(RED, f"ERREUR : {r['error']}")
            print(f"  {icon} Test {idx}/{total}  {msg}")
        elif r["passed"]:
            icon = _c(GREEN, "✓")
            print(f"  {icon} Test {idx}/{total}")
        else:
            icon  = _c(RED, "✗")
            inp   = _c(DIM, str(r["input"]))
            exp   = _c(GREEN, str(r["expected"]))
            actual = _c(RED, str(r["actual"]))
            print(f"  {icon} Test {idx}/{total}  entrée={inp}")
            print(f"            attendu={exp}  obtenu={actual}")

    print()
    bar_len   = 30
    filled    = int(bar_len * score / 100)
    bar_color = GREEN if score == 100 else (YELLOW if score >= 50 else RED)
    bar = _c(bar_color, "█" * filled) + _c(DIM, "░" * (bar_len - filled))
    print(f"  Score : [{bar}] {_c(BOLD + bar_color, str(score) + '%')}  ({passed}/{total} tests)")
    print()


def print_error(msg: str) -> None:
    print(f"\n  {_c(RED, '✗')} {msg}\n")


def print_success(msg: str) -> None:
    print(f"  {_c(GREEN, '✓')} {msg}")


def print_info(msg: str) -> None:
    print(f"  {_c(CYAN, '→')} {msg}")
