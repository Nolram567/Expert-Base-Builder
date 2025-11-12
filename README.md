# Expertbase Builder

Mit diesem Paket wird die [HERMES](https://hermes-hub.de/) Expertbase gebaut. Die HERMES Expertbase ist eine Personendatenbank für 
Forschende im Bereich der Digital Humanities, die auf der Grundlage von ORCID-Datensätzen gebaut wird.
Ziel und Zweck dieses Programmpakets sind, die HERMES Expertbase vollautomatisch auf Grundlage einer Eingabedatei mit
ORCID's zu bauen. Die Ausgabe ist eine mit Quarto Listings kompatible yaml-datei, eine qmd-datei für jeden Experten und
eine Log-Datei.

Perspektivisch soll für jeden Experten zudem ein JSON-LD erstellt und in die Dokumente eingebettet werden,
damit die Expertbase in den [Culture Knowledge Graph](https://nfdi4culture.de/de/dienste/details/culture-knowledge-graph.html) integriert werden kann.

Die HERMES Expertbase ist unter [https://hermes-hub.de/vernetzen/expertbase/](https://hermes-hub.de/vernetzen/expertbase/)
erreichbar.

## Ordnerstruktur

```plaintext
├── expert_base_builder/       # Alle Module des Pakets.
    ├── __init__.py                
    ├── expert.py                  # Das Modul enthält die Klasse Expert.
    ├── expert_base.py             # Dieses Modul enthält die Klasse Expertbase (Population, Bearbeiten, Parsen der Expertbase).
    └── orcid_aggregator.py        # Modul, für die Aggregation der ORCID-Daten.
├── data/                      # Eingabedateien
├── html/                      # HTML-Dateien
├── outputs/                   # Ausgabedateien
├── poetry.lock                # Poetry Lock-Datei, speichert die Abhängigkeiten mit festen Versionen
├── pyproject.toml             # Poetry-Projektkonfigurationsdatei
├── README.md                  # Projektdokumentation und Einführung
└── build_expert_base.py       # Dieses Skript baut die Expertbase.
```

## Installation und lokale Ausführung

Um das Projekt zu installieren, benutze `Poetry`, danach kann das Skript `build_expertbase.py` etwa in der Bash 
ausgeführt werden:

```bash
poetry install
python build_expertbase.py data/orcids.csv data/property_extension.csv outputs/expert_qmd outputs html/expert-template.qmd data/tadirah_tooltips.json
```

## Nutzung

Das Skript `build_expert_base.py` ist in die CI-Pipeline der Webseite von HERMES eingebunden. Es wird täglich 
automatisch (und bei Bedarf manuell) ausgeführt, übernimmt Änderungen aus den ORCID-Datensätzen oder erstellt neue 
Einträge. Das Skript kann auch lokal zu Debugging und Entwicklungszwecken eingesetzt werden; die Kommandozeilenargumente
müssen entsprechend angepasst werden.

## Abhängigkeiten

- Python 3.13 oder höher (Kompatibilität mit älteren Python-Versionen ist möglich, wurde aber nicht getestet)
- `requests`
- `pyyaml`
- `chevron`
- `beautifulsoup4`
