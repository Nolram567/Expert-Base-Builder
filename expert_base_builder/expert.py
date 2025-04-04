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
    Objekte dieser Klasse repräsentieren einen Experten der HERMES-Expert-Base.

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
        return self.properties.copy()

    def get_orcid(self) -> str:
        """
        Diese Methode gibt die ORCID des Expertenobjekts zurück.
        """
        return self.orcid

    def get_name(self, formated: bool = True) -> str or tuple[str, str]:
        """
        Diese Methode gibt den Namen des Expertenobjekts zurück.

        Args:
            formated: Spezifiziert, ob der Name als Einzelstring formatiert zurückgegeben werden soll oder als Tupel mit dem Vor- und Nachnamen.
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
        Die Methode greift auf das Modul llm_transformer zurück, um aus strukturierten Daten natürliche Sprache zu generieren.

        Args:
            formated: Spezifiert, ob die Rückgabe in natürlicher Sprache formatiert sein soll.
            n: Spezifiziert, wie viele Beschäftigungsverhältnisse maximal aufgenommen werden sollen.

        Returns:
            Die derzeitigen Beschäftigungsverhältnisse als Auflistung in natürlicher Sprache aus als Liste aus Tripeln mit Strings.
        """
        current_employment = self.properties.get("Derzeitige Beschäftigung", [])

        if formated:

            current_employment_string = ""

            for i in range(len(current_employment)):
                if i == n:
                    break
                if i == 0:
                    current_employment_string = (f"* {current_employment[i][0] if current_employment[i][0] else ''}"
                                                 f" ({current_employment[i][2] if current_employment[i][2] else ''})")
                else:
                    current_employment_string += (f"\n* {current_employment[i][0] if current_employment[i][0] else ''}"
                                                  f" ({current_employment[i][2] if current_employment[i][2] else ''})")

            return current_employment_string

        else:
            return self.properties.get("Derzeitige Beschäftigung", [])[:n]

    def get_mail(self) -> str:
        """
        Diese Methode gibt die E-Mail-Adresse des Experten als String zurück.

        Returns:
            Die E-Mail-Adresse oder einen leeren String.
        """
        return self.properties.get("E-Mail", "")

    def get_organisation(self) -> List[str]:
        """
        Die Methode gibt die Organisationen zurück, an denen der Experte derzeit beschäftigt ist.
        """
        current_employment = self.properties.get("Derzeitige Beschäftigung", [])
        organisations = []

        for employment in current_employment:
            if employment[2] not in organisations:
                organisations.append(employment[2])

        return organisations

    def get_research_interest(self, formated=True) -> List[str] or str:
        """
        Die Methode gibt die Forschungsinteressen (ORCID-Keywords) des Experten zurück.

        Args:
            formated: Falls True, werden die Keywords zu einem String konkateniert und mit Kommata getrennt.
        """

        if formated:
            orcid_keywords = self.properties.get("Forschungsinteressen", [])

            if len(orcid_keywords) == 1 and "," in orcid_keywords[0]:
                orcid_keywords = [k.strip() for k in orcid_keywords[0].split(",")]

            return ";".join(orcid_keywords)
        else:
            return self.properties.get("Forschungsinteressen", [])

    def get_tadirah(self, formated=True) -> list[str] or str:

        if formated:
            tadirah = self.properties.get("TaDiRAH-Zuordnung", [])
            return ";".join(tadirah)
        else:
            return self.properties.get("TaDiRAH-Zuordnung", "")

    def extend_properties(self, property: str, value) -> None:
        """
        Die Methode erweitert oder ersetzt die Eigenschaften des Expertenobjekts.

        Args:
            property: Der Name der Eigenschaft.
            value: Der Wert der Eigenschaft.
        """
        self.properties[property] = value

    def parse_qmd(self, path: str) -> None:
        """
        Die Methode generiert auf der Grundlage des Expertenobjekts eine qmd-Seite für den HERMES Hub.

        Args:
            path: Der relative Pfad des qmd-Dokuments
        """

        logger.info(f"Das qmd-Dokument für {self.get_name()} wird erstellt...")

        with open("html/expert-template.qmd", "r", encoding="utf-8") as qmd_template:
            template = qmd_template.read()

        formated_research_interest = Expert.__format_qmd_keywords(self.get_research_interest(formated=False))
        formated_tadirah = Expert.__format_tadirah_keywords(self.get_tadirah(formated=False))


        formated_template = chevron.render(
            template,
            {
                "expert-name": self.get_name(),
                "orcid-domain": f"https://orcid.org/{self.get_orcid()}",
                "current-employment": self.get_current_employment(n=3),
                "keywords": formated_research_interest,
                "tadirah": formated_tadirah,
                "e-mail": self.get_mail()
            },
        )

        output_path = os.path.join(path,
                            f"{self.get_name(formated=False)[0].lower().strip().replace(" ", "-")}"
                            f"-"
                            f"{self.get_name(formated=False)[1].lower().strip().replace(" ", "-")}"
                            f".qmd")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formated_template)

        logger.info(
            f"Das qmd-Dokument für {self.get_name()} wurde erstellt und unter {output_path} gespeichert..."
        )

    @staticmethod
    def __format_qmd_keywords(keywords: List[str]) -> str:

        if len(keywords) == 1 and "," in keywords[0]:
            keywords = [k.strip() for k in keywords[0].split(",")]

        builder = ['<div class="orcid-keywords">']
        builder.extend(f'<span class="tag">{word}</span>' for word in keywords)
        builder.append("</div>")

        return "".join(builder)

    @staticmethod
    def __format_tadirah_keywords(keywords: List[str]) -> str:

        if len(keywords) == 1 and "," in keywords[0]:
            keywords = [k.strip() for k in keywords[0].split(",")]

        builder = ['<div class="tadirah-keywords">']
        builder.extend(f'<span class="tag_tadirah">{word}</span>' for word in keywords)
        builder.append("</div>")

        return "".join(builder)

    def set_semantic_properties(self):
        pass
