import os

from .orcid_aggregator import *
from expert_base_builder.expert import Expert
import logging
import yaml
import json

logger = logging.getLogger(__name__)

class ExpertBase:
    """
    Objekte dieser Klasse repräsentieren die Expert Base als Bündel von Experten

    Diese Klasse stellt Methoden zur Verfügung, um die Expert Base zu erstellen, zu verwalten und zu serialisieren.
    Die Expert Base wird in der Objektvariable "base" als Dictionary nach folgendem Muster verwaltet:
    {orcid: Objekt der Klasse Experte,
    (...)
    }
    """

    def __init__(self, filename: str, from_csv: bool = True):
        """
        Der Konstruktor der Klasse enthält eine Fallunterscheidung. Entweder wird das ExpertBase-Objekt auf der Grundlage
        von einer CSV-Datei gefüllt oder aus dem Speicher geladen.

        Args:
            filename: Der Name der Quelldatei.
            from_csv: Wenn True, dann wird das Objekt mit einer CSV-Datei befüllt.
        """
        self.raw_base = {}
        self.base = {}

        if from_csv:
            self.populate_from_csv(filename)
        else:
            self.deserialize_expert_base(filename)

    def populate_from_csv(self, path: str) -> None:
        """
        Diese Methode füllt das ExpertBase-Objekt auf Grundlage einer CSV-Datei mit ORCID's.
        Die CSV-Datei muss die folgende Struktur haben:\n
        |Spaltenname1|Spaltenname2|\n
        |    Name    |   Orcid    |

        Args:
            path: Der Dateipfad zu der CSV-Datei.
        """

        orcids = read_orcids_from_csv(path)

        logger.info(f"Das Expert-Base-Objekt wird mit den ORCID's aus {path} befüllt.")

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
            extracted_mail = extract_mail(person_endpoint_data)

            new_expert = Expert(orcid=orcid,
                                data={
                                    "Vorname": extracted_name["given-names"],
                                    "Nachname": extracted_name["family-name"],
                                    "Derzeitige Beschäftigung": extracted_employment,
                                    "Forschungsinteressen": extracted_keywords,
                                    "E-Mail": extracted_mail,
                                    "Veröffentlichungen": extracted_work
                                })

            self.base[orcid] = new_expert
            self.raw_base[orcid] = new_expert.get_properties()

        logger.info(f"Das Expert-Base-Objekt wurde erfolgreich mit den ORCID's aus {path} befüllt.")

    def get_base(self) -> dict:
        """
        Gibt die Objektvariable base zurück.
        """
        return self.base.copy()

    def get_expert_as_list(self) -> List[Expert]:
        """
        Die Methode gibt alle Experten des ExpertBase Objekts als Liste zurück
        """
        return list(self.base.values())

    def get_orcids_as_list(self) -> List[str]:
        """
        Die Methode gibt die ORCIDs aller Experten in der Expert Base zurück.
        """
        return list(self.base.keys())

    def deserialize_expert_base(self, path: str) -> None:
        """
        Die Methode deserialisiert ein Expert Base Objekt.

        Args:
            path: Der Dateipfad, unter dem das Expert Base Objekt abgespeichert werden soll.
        """
        try:
            with open(path, "r", encoding='utf-8') as f:
                self.raw_base = json.load(f)

            for orcid, expert in self.raw_base.items():

                new_expert = Expert(orcid=orcid,
                                    data={
                                        "Vorname": expert.get("Vorname", ""),
                                        "Nachname": expert.get("Nachname", ""),
                                        "Derzeitige Beschäftigung": expert.get("Derzeitige Beschäftigung", []),
                                        "Forschungsinteressen": expert.get("Forschungsinteressen", []),
                                        "Veröffentlichungen": expert.get("Veröffentlichungen", []),
                                        "E-Mail": expert.get("E-Mail", "")
                                    })

                self.base[orcid] = new_expert

            logger.info(f"Das Expert Base Objekt wurde erfolgreich von {path} eingelesen.")

        except IOError as e:

            logger.error(f"Fehler beim Deserialisieren der Expert Base unter {path}:\n{e}")

    def serialize_expert_base(self, path: str, name: str) -> None:
        """
        Diese Methode serialisiert das Expert Base Objekt als JSON-Datei.

        Args:
            path: Der Dateipfad, unter dem das Expert Base Objekt serialisiert werden soll.
        """

        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, name), "w", encoding='utf-8') as f:
            json.dump(self.raw_base, f, indent=4, ensure_ascii=False)

        logger.info(f"Das Expert Base Objekt wurde erfolgreich unter {path} serialisiert.")

    def add_properties_from_csv(self, path: str) -> None:
        """
        Mit dieser Datei können die Eigenschaften der Experten in der Expert Base erweitert oder überschrieben werden.
        Die Eigenschaften werden in einer CSV-Datei nach dem folgenden Muster definiert:

        | name | orcid | neue_eigenschaft | neue_eigenschaft_2|(...)\n
        | (...) | (...) | keyword or keyword1, keyword2, (...)|(...)|(...)\n
        (...)

        Args:
             path: Der Dateipfad zu der CSV-Datei.
        """
        try:
            csv_file = open(path, newline='', encoding='utf-8')
            reader = csv.reader(csv_file)
            properties = next(reader)
            orcids = self.get_orcids_as_list()
        except IOError as e:
            logger.error(f"Die Datei {path} konnte nicht geöffnet werden:\n {e}")
            return

        if len(properties) < 2:
            logger.warning(f"Die CSV-Datei ist ungültig. Es muss mindestens 3 Spalten geben. Abbruch...")
            return
        elif not properties[1].lower() == "orcid":
            logger.warning(f"Die CSV-Datei ist ungültig. In der zweiten Spalte muss die ORCID stehen und die Spalte"
                         f" muss gültig benannt sein.")
            return

        for row in reader:

            current_orcid = row[1]

            if current_orcid in orcids:
                current_expert = self.base[current_orcid]
                for i, property in enumerate(properties[2:], 1):

                    new_properties = ""
                    if "," in row[1+i]:
                        new_properties = row[1+i].split(",")
                        new_properties = [p.strip() for p in new_properties]

                    current_expert.extend_properties(property, new_properties)

                    self.raw_base[current_orcid][property] = new_properties

                    logger.info(f"Für den Experten {current_orcid} wurde die Eigenschaft '{property}'"
                                f" mit dem Wert '{new_properties}' angelegt oder überschrieben.")
            else:
                logger.warning(f"Der Experte {current_orcid} ist noch nicht Teil der Expert Base.")

    def pretty_print(self) -> None:
        """
        Diese Methode druckt die Expert Base lesbar auf der Konsole.
        """
        print(json.dumps(self.raw_base, indent=4, ensure_ascii=False))

    def parse_yml(self, path: str) -> None:
        """
        Diese Methode parst ein ExpertBase-Objekt zu einer Yaml-Datei, die mit quarto listings kompatibel ist.

        Args:
            path: Der Dateipfad und der Name der Ausgabedatei.
        """

        logger.info(f"Das Expert-Base-Objekt wird zu einer YAML-Datei geparst.")

        entries = []

        for expert in self.get_expert_as_list():

            name = expert.get_name(formated=False)
            research_interest = expert.get_research_interest(formated=True)
            personal_page = f"experts/{name[0].lower().strip().replace(" ", "-")}-{name[1].lower().strip().replace(" ", "-")}.html"
            linked_name = f'<a href={personal_page}>{expert.get_name(formated=True)}</a>'
            organisation = ",<br>".join(expert.get_organisation())

            listing_entry = {
                "Name": linked_name,
                "Sortierschlüssel": expert.get_properties().get("Nachname", ""),
                "Organisation": organisation,
                "ORCID-Keywords": research_interest,
                "TaDiRAH-Zuordnung": expert.get_tadirah(formated=True),
                "Personenseite": f"{personal_page}"
                }

            entries.append(listing_entry)

        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, "expertbase.yml"), "w", encoding="utf-8") as f:
            yaml.dump(entries, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        logger.info(f"Das Expert-Base-Objekt wurde erfolgreich zu einer YAML-Datei geparst und unter {path} gespeichert.")
