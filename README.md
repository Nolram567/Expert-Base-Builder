# Expert Base Builder

Mit diesem Paket wird die [HERMES](https://hermes-hub.de/) Expert Base gebaut.
Ziel und Zweck dieses Programmpakets sind, die HERMES Expert Base vollautomatisch auf Grundlage einer Eingabedatei mit
ORCID's zu bauen. Die Ausgabe ist eine mit quarto listings kompatible yaml-datei und eine qmd-datei für jede:n Expert:in. 
Perspektivisch soll für jede:n Expert:in zudem ein JSON-LD erstellt und in die Dokumente eingebettet werden, damit die Expert Base in den [Culture Knowledge Graph](https://nfdi4culture.de/de/dienste/details/culture-knowledge-graph.html) integriert werden kann.

Das Programmpaket befindet sich derzeit im frühen Entwicklungsstadium.

## Ordnerstruktur

```plaintext
├── expert_base_builder/       # Alle Module des Pakets.
    ├── __init__.py                
    ├── expert.py                  # Das Modul enthält die Klasse Expert.
    ├── expert_base.py             # Dieses Modul enthält die Klasse Expert Base (Population, Bearbeiten, Parsen der Expert Base).
    ├── llm_transformer.py         # Modul für die Transformation von strukturierten Daten in natürliche Sprache.
    └── orcid_aggregator.py        # Modul, für die Aggregation der ORCID-Daten.
├── data/                      # Eingabedateien
├── html/                      # HTML-Dateien
├── outputs/                   # Ausgabedateien
├── poetry.lock                # Poetry Lock-Datei, speichert die Abhängigkeiten mit festen Versionen
├── pyproject.toml             # Poetry-Projektkonfigurationsdatei
├── README.md                  # Projektdokumentation und Einführung
├── build_expert_base.py       # Dieses Skript baut die Expert Base.
└── extend_expert_base.py      # Dieses Skript erweitert die Expert Base.
```

## Installation

Um das Projekt zu installieren, benutze `Poetry`:

```bash
poetry install
```

## Nutzung

Die zwei ausführbaren Skipte, welche die Expert Base bauen und erweitern, befindet sich in den Skripten `build_expert_base.py` und `extend_expert_base.py`

```python
import logging
from expert_base_builder.expert_base import ExpertBase


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(csv_file: str, output_qmd: str, output_yml: str, base_url: str) -> None:
    try:
        logger.info(f"Starte die Verarbeitung der Expert Base mit der Datei: {csv_file}")

        expert_base = ExpertBase(csv_file, from_csv=True)

        expert_base.add_properties_from_csv("data/property_extension.csv")

        expert_base.serialize_expert_base("saved_base/backup.json") # Serialisiere die Expert Base als JSON für die Begutachtung.

        # Für jeden Experten eine QMD-Datei erstellen
        for e in expert_base.get_expert_as_list():
            e.parse_qmd(output_qmd)

        # Expert Base als YAML-Datei speichern
        expert_base.parse_yml(output_yml, url=base_url)

    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}", exc_info=True)


if __name__ == "__main__":

    main(
        csv_file="data/orcids.csv",
        output_qmd = "outputs/expert_qmd",
        output_yml = "outputs/expert_base.yml",
        base_url = "https://hermes-hub-development-repo-e9c5dc.pages.uni-marburg.de"
    )

```

## Abhängigkeiten

- Python 3.13 oder höher
- `requests`
- `pyyaml`
- `chevron`
- `beautifulsoup4`

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.
