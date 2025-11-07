import sys

import logging

import expert_base_builder.expert
from expert_base_builder.expert_base import ExpertBase

'''
Konfiguration des Loggers: Die Ausgaben werden sowohl auf der Konsole gedruckt als auch in die Datei "build_expert_base.log"
geschrieben, die in der CI-Pipeline als Artefakt gespeichert wird.
'''
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("build_expert_base.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

def main(csv_file: str, csv_extension: str, output_qmd: str, output_yml: str, tadirah_tooltips_path: str) -> None:
    try:
        logger.info(f"Starte die Verarbeitung der Expert Base mit der Datei: {csv_file}")

        expert_base_builder.expert.Expert.tadirah_tooltips_path = tadirah_tooltips_path

        expert_base = ExpertBase(csv_file, from_csv=True)

        expert_base.serialize_expert_base(path="saved_base", name="backup.json") # Serialisiere die Expert Base als JSON für die Begutachtung.

        expert_base.add_properties_from_csv(path=csv_extension)

        # Für jeden Experten eine QMD-Datei erstellen
        for e in expert_base.get_expert_as_list():
            e.parse_qmd(output_directory_path=output_qmd, chevron_template_path="Expert-Base-Builder/html/expert-template.html")

        # Expert Base als YAML-Datei serialisieren
        expert_base.parse_yml(path=output_yml)

    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten:", exc_info=True)
        raise


if __name__ == "__main__":

    if not len(sys.argv) == 6:
        logger.error("Die Zahl der übergebenen Argumente ist nicht korrekt, es werden genau 5 erwartet; übergeben wurden"
                     f" {len(sys.argv)} Argumente.")
        sys.exit(1)

    main(
        csv_file=sys.argv[1],  # orcids
        csv_extension=sys.argv[2],  # property_extension.
        output_qmd=sys.argv[3],  # Ausgabeordner für die Detailseiten.
        output_yml=sys.argv[4], # Ausgabeordner für die yml-Datei.
        tadirah_tooltips_path= sys.argv[5] # Pfad zur tadirah-Datei
    )

    # python build_expertbase.py data/orcids.csv data/property_extension.csv outputs/expert_qmd outputs/expertbase.yml data/tadirah_tooltips.json
    # python Expert-Base-Builder/build_expertbase.py config/orcids.csv config/property_extension.csv Expert-Base-Builder/outputs/ Expert-Base-Builder/outputs/experts