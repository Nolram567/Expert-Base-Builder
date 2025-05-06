import logging

from expert_base_builder.expert_base import ExpertBase

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("extend_expert_base.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def main(input_path: str, output_path:str, properties: str) -> None:
    try:
        logger.info(f"Starte die Erweiterung der Expert Base mit der Datei: {properties}")

        expert_base = ExpertBase(input_path, from_csv=False)

        expert_base.add_properties_from_csv(properties)

        expert_base.serialize_expert_base("output_path")

    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}", exc_info=True)


if __name__ == "__main__":

    main(input_path="saved_base/expert_base.json",
         output_path="saved_base/expert_base.json",
         properties="data/property_extension.csv")
