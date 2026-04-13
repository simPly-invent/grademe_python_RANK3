# 📋 grademe_python

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ██████╗  █████╗ ██████╗ ███████╗███╗   ███╗███████╗   ║
║  ██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔════╝████╗ ████║██╔════╝   ║
║  ██║  ███╗██████╔╝███████║██║  ██║█████╗  ██╔████╔██║█████╗     ║
║  ██║   ██║██╔══██╗██╔══██║██║  ██║██╔══╝  ██║╚██╔╝██║██╔══╝     ║
║  ╚██████╔╝██║  ██║██║  ██║██████╔╝███████╗██║ ╚═╝ ██║███████╗   ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝     ╚═╝╚══════╝   ║
║                                                                  ║
║              Clone d'examshell — Rank 03 · Python                ║
║                      by mobenais @ 42                            ║
╚══════════════════════════════════════════════════════════════════╝
```

> ⚠️ **Projet non officiel** — Outil d'entraînement personnel, sans affiliation avec l'école 42.

---

## 📌 Présentation

**grademe_python** est un clone local d'`examshell` conçu pour s'entraîner aux exercices Python du **Rank 03** de l'école 42.  
Il reproduit le workflow de l'examen réel : sujet aléatoire, fichier à rendre dans `rendu/`, correction automatique, score en pourcentage.

Il embarque également :
- une **interface TUI interactive** (navigation clavier)
- un **mode challenge** (tous les sujets, easy → medium → hard)
- un **historique** des sessions passées

---

## 🗂️ Structure du projet

```
grademe_python/
├── Makefile              ← Commandes principales
├── requirements.txt      ← Aucune dépendance externe
├── examshell.py          ← CLI (start / status / grademe / finish)
├── grader.py             ← Correcteur automatique (subprocess isolé)
├── display.py            ← Affichage coloré ANSI
├── menu.py               ← Interface TUI interactive
├── subjects/
│   └── rank03.json       ← 12 sujets avec tests
├── sessions/             ← Historique des sessions (auto-créé)
└── rendu/                ← Ton fichier Python à rendre (auto-créé)
```

---

## ⚙️ Prérequis

| Outil     | Version minimale |
|-----------|-----------------|
| Python    | ≥ 3.10          |
| Make      | any             |
| OS        | Linux / macOS   |

> `termios` et `tty` (navigation clavier du TUI) ne sont **pas disponibles sur Windows**.

Aucune dépendance externe — zéro `pip install`.

---

## 🚀 Installation

```bash
git clone https://github.com/mobenais/grademe_python.git
cd grademe_python
make
```

C'est tout.

---

## 🎮 Utilisation

### Interface interactive (recommandé)

```bash
make
```

Navigation avec `↑` `↓` et `Entrée`. Quatre modes disponibles depuis le menu :

| Option | Description |
|--------|-------------|
| Commencer un examen | Sujet aléatoire (filtre difficulté optionnel) |
| Mode entraînement | Tu choisis le sujet dans la liste |
| Mode challenge | Tous les sujets, easy → medium → hard |
| Historique | Tableau des sessions passées |

---

### CLI directe

```bash
make exam          # Examen rapide — sujet aléatoire
make challenge     # Mode challenge complet
make status        # Session en cours + chrono
make grademe       # Corriger le fichier dans rendu/
make finish        # Terminer la session
make history       # Sessions passées
make clean         # Reset session + rendu/
make help          # Afficher l'aide
```

Ou directement via Python :

```bash
python3 examshell.py start          # sujet aléatoire
python3 examshell.py start -d easy  # filtre par difficulté
python3 examshell.py grademe
python3 examshell.py finish
```

---

## 🧪 Workflow typique

```
1.  make                         # Lance le menu
2.  → Commencer un examen        # Choisir la difficulté
3.  Ouvre rendu/<sujet>.py       # Dans ton éditeur
4.  Code ta solution
5.  make grademe                 # Correction automatique
6.  → 100% ?  make finish        # Bilan + sauvegarde
```

---

## 📚 Sujets disponibles (Rank 03)

| # | Sujet | Difficulté |
|---|-------|-----------|
| 01 | Number Base Converter | 🟡 Medium |
| 02 | Mirror Matrix | 🟢 Easy |
| 03 | Bracket Validator | 🟡 Medium |
| 04 | Is Anagram | 🟢 Easy |
| 05 | Alternate Case | 🟢 Easy |
| 06 | Caesar Cipher | 🟢 Easy |
| 07 | Sort Words | 🔴 Hard |
| 08 | Is Palindrome | 🟢 Easy |
| 09 | Find Runner Up | 🟢 Easy |
| 10 | Count Islands | 🔴 Hard |
| 11 | Longest Consecutive | 🔴 Hard |
| 12 | Matrix Transposition | 🟢 Easy |

---

## 🔧 Correcteur automatique

Le correcteur (`grader.py`) exécute ta fonction dans un **subprocess isolé** avec un timeout de 5 secondes.  
Il compare les sorties aux résultats attendus et retourne un score en pourcentage.

```
  ✓ Test 1/4
  ✓ Test 2/4
  ✗ Test 3/4  attendu=True  obtenu=None
  ✓ Test 4/4

  Score : [████████████████████░░░░░░░░░░] 75%  (3/4 tests)
```

---

## 📝 Ajouter des sujets

Les sujets sont définis dans `subjects/rank03.json`.  
Chaque entrée suit ce format :

```json
{
  "id": "py_mon_sujet",
  "title": "Mon Sujet",
  "difficulty": "easy",
  "assignment": "Description de l'exercice.",
  "signature": "def mon_sujet(x: int) -> int:",
  "tests": [
    {"input": [[42]], "expected": 84}
  ]
}
```

---

## 👤 Auteur

| | |
|---|---|
| **Login** | mobenais |
| **École** | 42 |
| **Projet** | grademe_python |

---

## ⚖️ Licence

Projet personnel open source — pas de droits réservés.  
Les sujets sont inspirés du contenu pédagogique de l'école 42 (non officiel).

---

*Made with ☕ and `python3` by mobenais*