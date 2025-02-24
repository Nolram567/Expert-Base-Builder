import logging
from expert_base_builder.expert_base import ExpertBase


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

def main(csv_file: str, output_qmd: str, output_yml: str) -> None:
    try:
        logger.info(f"Starte die Verarbeitung der Expert Base mit der Datei: {csv_file}")

        expert_base = ExpertBase("data/orcids.csv", from_csv=True)

        expert_base.serialize_expert_base("saved_base/expert_base.json")

        # Für jeden Experten eine QMD-Datei erstellen
        for e in expert_base.get_expert_as_list():
            e.parse_qmd(output_qmd)

        # Expert Base als YAML-Datei speichern
        expert_base.parse_yml(output_yml)

    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {e}", exc_info=True)


if __name__ == "__main__":

    csv_file = "data/orcids.csv"
    output_qmd = "outputs/expert_qmd"
    output_yml = "expert_base.yml"

    main(csv_file, output_qmd, output_yml)
