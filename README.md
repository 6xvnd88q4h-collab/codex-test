# codex-test

Ein kleines Kommandozeilenwerkzeug für Handwerksbetriebe. Projekte,
Aufgaben und Materialbedarf werden in einer JSON-Datei gespeichert und
können über die folgenden Befehle verwaltet werden:

```bash
# Neues Projekt anlegen
python handwerk_app.py project add "Badsanierung" "Firma Beispiel" --address "Musterstraße 1" --due-date 2024-05-31

# Aufgabe zum Projekt hinzufügen
python handwerk_app.py task add 1 "Elektrik prüfen" --due-date 2024-03-15

# Materialbedarf hinterlegen (optional projektbezogen)
python handwerk_app.py material add "Fliesen weiß" 20 --unit qm --project-id 1

# Übersicht
python handwerk_app.py project list
python handwerk_app.py project detail 1
python handwerk_app.py inventory list
```

Die Daten landen standardmäßig in `handwerk_data.json` im Projektordner
und können direkt als einfache Einsatzübersicht genutzt werden.
