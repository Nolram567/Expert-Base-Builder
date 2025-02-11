from .orcid_aggregator import *
from expert_base_builder.expert import Expert
import os
import logging
import yaml

logger = logging.getLogger(__name__)

class ExpertBase():
    """
    Objekte dieser Klasse repräsentieren die Expert Base als Bündel von Experten

    Diese Klasse stellt Methoden zur Verfügung, um die Expert Base zu erstellen, zu verwalten und zu serialisieren.
    Die Expert Base wird in der Objektvariable "base" als Dictionary nach folgendem Muster verwaltet:
    {orcid: Objekt der Klasse Experte,
    (...)
    }

    Die Klassenvariable "PATH" enthält den Pfad zu dem Verzeichnis, in dem die Quell-CSV-Datei oder serialisierte Objekte liegen.
    Die Klassenvariable PROPERTIES enthält alle zulässigen Eigenschaften.
    """

    INPUT_PATH = "data"
    OUTPUT_PATH = "outputs"
    PROPERTIES = ["Vorname", "Nachname", "Derzeitige Beschäftigung", "Forschungsinteressen"]

    def __init__(self, filename: str, from_csv: bool = True):
        """
        Der Konstruktor der Klasse enthält eine Fallunterscheidung. Entweder wird das ExpertBase-Objekt auf der Grundlage
        von einer CSV-Datei gefüllt oder aus dem Speicher geladen.

        Args:
            filename: Der Name der Quelldatei.
            from_csv: Wenn True, dann wird das Objekt mit einer CSV-Datei befüllt.
        """
        if from_csv:
            self.populate_from_csv(filename)
        else:
            self.deserialize_expert_base(filename)

    def populate_from_csv(self, filename: str) -> None:
        """
        Diese Methode füllt das ExpertBase-Objekt auf Grundlage einer CSV-Datei mit ORCID's.
        Die CSV-Datei muss die folgende Struktur haben:\n
        |Spaltenname1|Spaltenname2|\n
        |    Name    |   Orcid    |
        """

        full_path = os.path.join(ExpertBase.INPUT_PATH, filename)
        orcids = read_orcids_from_csv(full_path)
        self.base = {}
        self.raw_base = {}

        logger.info(f"Das Expert-Base-Objekt wird mit den ORCID's aus {full_path} befüllt.")

        for orcid in orcids:
            logger.info(f"Abfrage von ORCID {orcid}...")
            person_endpoint_data = fetch_orcid_data(orcid, endpoint="person")
            activities_endpoint_data = fetch_orcid_data(orcid, endpoint="activities")


            if person_endpoint_data is None or activities_endpoint_data is None:
                logger.error(f"Fehler beim Abrufen von Daten oder leere Antwort für ORCID {orcid}")
                continue

            extracted_name = extraxt_names(person_endpoint_data)
            extracted_keywords = extract_keywords(person_endpoint_data)
            extracted_employment = extract_current_employments(activities_endpoint_data)
            extracted_work = extract_work_doi(activities_endpoint_data, n = 10)

            new_expert = Expert(orcid=orcid,
                                data={
                                    "Vorname": extracted_name["given-names"],
                                    "Nachname": extracted_name["family-name"],
                                    "Derzeitige Beschäftigung": extracted_employment,
                                    "Forschungsinteressen": extracted_keywords,
                                    "Veröffentlichungen": extracted_work
                                })

            self.base[orcid] = new_expert
            self.raw_base[orcid] = new_expert.get_properties()

        logger.info(f"Das Expert-Base-Objekt wurde erfolgreich mit den ORCID's aus {full_path} befüllt.")

    def get_base(self) -> dict:
        """
        Gibt die Objektvariable base zurück.
        """
        return self.base

    def get_expert_as_list(self) -> List[Expert]:
        """
        Die Methode gibt alle Experten des ExpertBase Objekts als Liste zurück
        """
        return list(self.base.values())

    def deserialize_expert_base(self, filename: str):
        pass

    def serialize_expert_base(self, filename: str) -> int:
        pass

    def add_properties_from_csv(self, filename: str) -> int:
        pass

    def pretty_print(self) -> None:
        """
        Diese Methode druckt das ExpertBase lesbar auf der Konsole.
        """
        print(json.dumps(self.raw_base, indent=4, ensure_ascii=False))

    def parse_yml(self, output_file) -> None:
        """
        Diese Methode parst ein ExpertBase-Objekt zu einer Yaml-Datei, die mit quarto listings kompatibel ist.

        Args:
            output_file: Der Dateipfad und der Name der Ausgabedatei.
        """

        logger.info(f"Das Expert-Base-Objekt wird zu einer YAML-Datei geparst.")

        entries = []

        for expert in self.get_expert_as_list():

            name = expert.get_name(formated=False)
            research_interest = expert.get_research_interest(formated=True)
            orcid = f'<p><a href="https://orcid.org/{expert.get_orcid()}">{expert.get_orcid()} <img src="orcid.png" alt="orcid" width="16" height="16"></a></p>'
            linked_name = f'<a href="www.hermes-hub.de/vernetzen/experts/{name[0]}-{name[1]}.html">{expert.get_name(formated=True)}</a>'
            employment = expert.get_current_employment(n = 1, formated=True)

            listing_entry = {
                "Name": linked_name,
                "Beschäftigung": employment,
                "Forschungsfelder": research_interest,
                "ORCID": orcid,
                "HERMES-Affiliation": "",
                "TaDiRAH-Zuordnung": ""
                }

            entries.append(listing_entry)

        full_path = os.path.join(ExpertBase.OUTPUT_PATH, output_file)

        with open(full_path, "w", encoding="utf-8") as f:
            yaml.dump(entries, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        logger.info(f"Das Expert-Base-Objekt wurde erfolgreich zu einer YAML-Datei geparst und unter {full_path} gespeichert.")
