import logging
from expert_base_builder.expert_base import ExpertBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(base_path: str, properties: str) -> None:
    try:
        logger.info(f"Starte die Erweiterung der Expert Base mit der Datei: {properties}")

        expert_base = ExpertBase(base_path, from_csv=False)

        expert_base.add_properties_from_csv(properties)

        expert_base.serialize_expert_base("saved_base/expert_base.json")

    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {e}", exc_info=True)


if __name__ == "__main__":

    main("saved_base/expert_base.json",
         "data/property_extension.csv")
