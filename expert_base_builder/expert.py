import os
from typing import List
import chevron
import requests
import html
from bs4 import BeautifulSoup
import logging

from .llm_transformer import triple_to_nl_sentence

logger = logging.getLogger(__name__)


class Expert:
    """
    Objekte dieser Klasse repräsentieren einen Experten der HERMES-Expertbase.

    Diese Klasse stellt Methoden zur Verfügung, um einzelne Experten zu erstellen, zu verwalten und in semantische
    Repräsentationen zu übersetzen.

    Die Objektvariable "orcid" ist die ORCID des Experten.
    Die Objektvariable "properties" enthält alle definierten Eigenschaften des Experten als Dictionary nach dem Muster:
    {
        'Vorname': '(...)',
        'Nachname': '(...)',
        'Derzeitige Beschäftigung': [['(...)', '(...)', '(...)'], (...)],
        'Forschungsinteressen': ['(...)', '(...)', '(...)'],
        (...)
    }
    """

    def __init__(self, orcid: str, data: dict):
        """
        Der Konstruktor der Klasse.

        Args:
            orcid: Die ORCID des Expertenobjekts.
            data: Die Eigenschaften des Expertenobjekts als Dictionary.
        """
        self.orcid = orcid
        self.properties = data

    def get_properties(self):
        """
        Diese Methode gibt die Eigenschaften des Expertenobjekts zurück.
        """
        return self.properties

    def get_orcid(self) -> str:
        """
        Diese Methode gibt die ORCID des Expertenobjekts zurück.
        """
        return self.orcid

    def get_name(self, formated: bool = True) -> str or tuple[str, str]:
        """
        Diese Methode gibt den Namen des Expertenobjekts zurück.

        Args:
            formated: Spezifiziert, ob die Rückgabe als Einzelstring formatiert zurückgegeben werden soll oder als Tupel mit dem Vor- und Nachnamen.
        """
        return (
            f"{self.properties.get('Vorname', '')} {self.properties.get('Nachname', '')}"
            if formated
            else [
                self.properties.get("Vorname", ""),
                self.properties.get("Nachname", ""),
            ]
        )

    def get_current_employment(
        self, n, formated=True
    ) -> str or list[tuple[str, str, str]]:
        """
        Diese Methode gibt die derzeitige Beschäftigung zurück. Entweder als Liste von Tripeln oder als String, der das
        oder die Arbeitsverhältnisse in natürlicher Sprache beschreibt.
        Die Methode greif auf das Modul llm_transformer zurück, um aus strukturierten Daten natürliche Sprache zu generieren.

        Args:
            formated: Spezifiert, ob die Rückgabe in natürlicher Sprache formatiert sein soll.
            n: Spezifiziert, wie viele Beschäftigungsverhältnisse maximal aufgenommen werden sollen.

        Returns:
            Die derzeitigen Beschäftigungsverhältnisse als auflistung in natürlicher Sprache aus als Liste aus Tripeln mit Strings.
        """
        current_employment = self.properties.get("Derzeitige Beschäftigung", [])

        if formated:

            current_employment_string = ""

            for i in range(len(current_employment)):
                if i == n:
                    break
                if i == 0:
                    current_employment_string = (
                        f"{triple_to_nl_sentence(current_employment[i])}"
                    )
                else:
                    current_employment_string = f"* {current_employment_string}\n* {triple_to_nl_sentence(current_employment[i])}"

            return current_employment_string
        else:
            return self.properties.get("Derzeitige Beschäftigung", [])[:n]

    def get_research_interest(self, formated=True) -> List[str] or str:
        if formated:
            return ", ".join(self.properties.get("Forschungsinteressen", []))
        else:
            return self.properties.get("Forschungsinteressen", [])

    def set_semantic_properties(self):
        pass

    def extend_properties(self):
        pass

    def parse_qmd(self, output_path) -> None:
        """
        Die Methode generiert auf der Grundlage des Experten-Objekts eine qmd-Seite für den HERMES Hub.

        Args:
            output_path: Der relative Pfad des qmd-Dokuments
        """

        logger.info(f"Das qmd-Dokument für {self.get_name()} wird erstellt...")

        with open("html/expert-template.qmd", "r", encoding="utf-8") as qmd_template:
            template = qmd_template.read()

        formated_template = chevron.render(
            template,
            {
                "expert-name": self.get_name(),
                "orcid-domain": f"https://orcid.org/{self.get_orcid()}",
                "current-employment": self.get_current_employment(n=3),
                "research-interest": self.get_research_interest(),
                "last-work": self.doi_resolver(),
            },
        )

        output_path = os.path.join(
            output_path,
            f"{self.get_name(formated=False)[0].lower()}-{self.get_name(formated=False)[1].lower()}.qmd",
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formated_template)

        logger.info(
            f"Das qmd-Dokument für {self.get_name()} wurde erstellt und unter {output_path} gespeichert..."
        )

    def doi_resolver(self) -> str:
        """
        Diese Helfermethode löst alle DOI's des Objekts zu einer Literaturangabe nach MLA auf.
        Die DOI's sollten unter self.properties['Veröffentlichung'] als Liste vorliegen.

        Returns:
            Alle aufgelösten Objekte als String zeilenweise nach MLA formatiert.
        """

        formated_publications = ""

        for doi in self.get_properties().get("Veröffentlichungen", []):

            logger.info(f"{doi} wird aufgelöst...")

            headers = {"Accept": "text/x-bibliography; style=mla"}

            response = requests.get(f"https://doi.org/{doi}", headers=headers)

            if response.status_code == 200:

                response.encoding = "utf-8"

                decoded_text = html.unescape(response.text)

                decoded_text = BeautifulSoup(decoded_text, "html.parser").get_text()

                formated_publications = f"{formated_publications}\n{decoded_text}"
            else:
                logger.error(
                    f"{doi} konnte nicht aufgelöst werden. Status-Code: {response.status_code}"
                )

        return formated_publications
