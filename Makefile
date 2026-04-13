## ╔══════════════════════════════════════╗
## ║   examshell · Rank 03 Python         ║
## ╚══════════════════════════════════════╝
##
##  Usage :
##    make              → Lance l'interface interactive (menu TUI)
##    make menu         → Idem
##    make exam         → Examen rapide (sujet aléatoire)
##    make challenge    → Mode challenge (easy → medium → hard)
##    make status       → Affiche la session en cours
##    make grademe      → Corrige ton fichier dans rendu/
##    make finish       → Termine la session en cours
##    make history      → Résumé des sessions passées
##    make clean        → Supprime la session en cours + rendu/
##    make help         → Affiche cette aide

PYTHON   := python3
SHELL_PY := examshell.py
MENU_PY  := menu.py

.PHONY: all menu exam challenge status grademe finish history clean help

## Cible par défaut : TUI interactif
all: menu

menu:
	@$(PYTHON) $(MENU_PY)

## Examen rapide — sujet aléatoire
exam:
	@$(PYTHON) $(SHELL_PY) start

challenge:
	@$(PYTHON) -c "\
import sys; sys.path.insert(0, '.'); \
from menu import screen_challenge, load_subjects; \
screen_challenge(load_subjects())"

status:
	@$(PYTHON) $(SHELL_PY) status

grademe:
	@$(PYTHON) $(SHELL_PY) grademe

finish:
	@$(PYTHON) $(SHELL_PY) finish

history:
	@$(PYTHON) -c "\
import sys; sys.path.insert(0, '.'); \
from menu import screen_history, SHOW_CURSOR; \
print(SHOW_CURSOR, end=''); \
screen_history()"

clean:
	@echo "Nettoyage de la session en cours et du dossier rendu/..."
	@rm -f sessions/current.json
	@rm -f rendu/*.py
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "OK"

help:
	@echo ""
	@echo "  ╔══════════════════════════════════════╗"
	@echo "  ║   examshell · Rank 03 Python         ║"
	@echo "  ╚══════════════════════════════════════╝"
	@echo ""
	@echo "  make              Lance l'interface interactive"
	@echo "  make exam         Examen rapide (sujet aléatoire)"
	@echo "  make challenge    Tous les sujets easy → hard"
	@echo "  make status       Session en cours + chrono"
	@echo "  make grademe      Corrige ton fichier rendu/"
	@echo "  make finish       Termine la session"
	@echo "  make history      Sessions passées"
	@echo "  make clean        Remet à zéro"
	@echo ""