# Expert Base Builder

Mit diesem Paket wird die [HERMES](https://hermes-hub.de/) Expertbase gebaut. Die HERMES Expertbase ist eine Personendatenbank für 
Forschende im Bereich der Digital Humanities, die auf der Grundlage von ORCID-Datensätzen gebaut wird.
Ziel und Zweck dieses Programmpakets sind, die HERMES Expertbase vollautomatisch auf Grundlage einer Eingabedatei mit
ORCID's zu bauen. Die Ausgabe ist eine mit quarto listings kompatible yaml-datei und eine qmd-datei für jede:n Expert:in. 
Perspektivisch soll für jede:n Expert:in zudem ein JSON-LD erstellt und in die Dokumente eingebettet werden,
damit die Expert Base in den [Culture Knowledge Graph](https://nfdi4culture.de/de/dienste/details/culture-knowledge-graph.html) integriert werden kann.

Die HERMES Expertbase ist unter [https://hermes-hub.de/vernetzen/expertbase/](https://hermes-hub.de/vernetzen/expertbase/)
erreichbar.

## Ordnerstruktur

```plaintext
├── expert_base_builder/       # Alle Module des Pakets.
    ├── __init__.py                
    ├── expert.py                  # Das Modul enthält die Klasse Expert.
    ├── expert_base.py             # Dieses Modul enthält die Klasse Expert Base (Population, Bearbeiten, Parsen der Expert Base).
    └── orcid_aggregator.py        # Modul, für die Aggregation der ORCID-Daten.
├── data/                      # Eingabedateien
├── html/                      # HTML-Dateien
├── outputs/                   # Ausgabedateien
├── poetry.lock                # Poetry Lock-Datei, speichert die Abhängigkeiten mit festen Versionen
├── pyproject.toml             # Poetry-Projektkonfigurationsdatei
├── README.md                  # Projektdokumentation und Einführung
└── build_expert_base.py       # Dieses Skript baut die Expert Base.
```

## Installation

Um das Projekt zu installieren, benutze `Poetry`:

```bash
poetry install
```

## Nutzung

Das Skript `build_expert_base.py` ist in die CI-Pipeline des HERMES-Hub eingebunden. Es existiert ein Branch für die
Pipeline (pipeline_branch) und ein Branch (master) für die Entwicklung, der ohne Modifikation lokal ausgeführt werden 
kann.

## Abhängigkeiten

- Python 3.13 oder höher
- `requests`
- `pyyaml`
- `chevron`
- `beautifulsoup4`
