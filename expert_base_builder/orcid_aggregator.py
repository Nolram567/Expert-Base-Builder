import csv
import json
from xml.etree.ElementTree import indent

import requests
import logging
from typing import List, Dict
from datetime import date

BASE_URL = "https://pub.orcid.org/v3.0/"

logger = logging.getLogger(__name__)

def read_orcids_from_csv(file_path: str) -> List[str]:
    """
    Liest ORCID-Bezeichner aus der zweiten Spalte einer CSV-Datei ein.

    Args:
        file_path: Pfad zur CSV-Datei.

    Returns:
        Liste der ORCID-Bezeichner.
    """
    orcids = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            orcids.append(row[1].strip())
    return orcids

def fetch_orcid_data(orcid: str, endpoint: str) -> dict or None:
    """
    Fragt Daten für eine Person über die ORCID API ab.

    Args:
        orcid: ORCID-Bezeichner.
        endpoint: Der Endpunkt, der abgefragt werden soll.
    Returns:
        ORCID-Daten als Dictionary oder None bei Fehler.
    """
    headers = {"Accept": "application/json"}
    url = f"{BASE_URL}{orcid}/{endpoint}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        logger.warning(f"Fehler beim Abrufen von ORCID {orcid}: {response.status_code}")
        return None

def extraxt_names(orcid_data: dict or None) -> Dict[str, str]:
    """
    Extrahiert die Namen aus einem Personendatensatz.

    Args:
        orcid_data: Die ORCID-Daten vom /person-Endpunkt der ORCID-API.

    Returns:
        Extrahierte Namen als Dictionary.
    """
    extracted = {}
    if not orcid_data:
        logger.warning("Der ORCID-Datensatz ist leer.")
        return {}

    names = orcid_data.get("name", {})
    extracted["given-names"] = names.get("given-names", {}).get("value", "N/A")
    extracted["family-name"] = names.get("family-name", {}).get("value", "N/A")

    return extracted

def extract_mail(orcid_data: dict or None) -> str:
    """
    Extrahiert die erste E-Mail-Adresse aus einem Personendatensatz.

    Args:
        orcid_data: Die ORCID-Daten vom /person-Endpunkt der ORCID-API.
    """
    emails = orcid_data.get("emails", {}).get("email", [])
    email_str = emails[0].get("email", "") if emails else ""
    return email_str

def extract_current_employments(orcid_data: dict or None) -> list:
    """
    Extrahiert die derzeit aktiven Beschäftigungsverhältnisse aus einem Personendatensatz.

    Args:
        orcid_data: Die ORCID-Daten vom /activities-Endpunkt der ORCID-API.

    Returns:
        Extrahierte Beschäftigungsverhältnisse als Dictionary.
    """
    current_employments = []

    for employment in orcid_data.get("employments", {}).get("affiliation-group", []):

        current_summary = employment.get("summaries", [])[0].get("employment-summary", {})

        # Wenn das Enddatum nicht definiert ist
        if current_summary["end-date"] is None:
            current_employments.append([current_summary.get("role-title", ""),
                                        current_summary.get("department-name", ""),
                                        current_summary.get("organization", {}).get("name", "")]
                                       )
            continue

        # übersprigen, wenn das Enddatum in der Vergangenheit liegt
        if int(current_summary["end-date"]["year"]['value']) < date.today().year:
            continue

        # Wenn das Enddatum in der Zukunft liegt
        year = int(current_summary.get('end-date')['year']['value'])
        month = int(current_summary.get('end-date')['month']['value'])
        day = int(current_summary.get('end-date')['day']['value'])

        given_date = date(year, month, day)
        today = date.today()

        if given_date > today:
            current_employments.append([current_summary.get("role-title", ""),
                                        current_summary.get("department-name", ""),
                                        current_summary.get("organization", {}).get("name", "")]
                                       )

    return current_employments

def extract_keywords(orcid_data: dict) -> List[str]:
    """
    Extrahiert eine Liste von Keywords aus einem Personendatensatz.

    Args:
       orcid_data (dict): Die ORCID-Daten vom /person-Endpunkt der ORCID-API.

    Returns:
       List[str]: Eine Liste mit den Keywords der jeweiligen Person als Strings.
    """
    keywords = []

    for k in orcid_data["keywords"]["keyword"]:
        keywords.append(k["content"])
    return keywords

def extract_work_doi(orcid_data: dict, n: int or float("inf")) -> List[str]:
    """
    Extrahiert die DOI der Publikationen aus einem Aktivitätendatensatz.

    Args:
        orcid_data: Die ORCID-Daten vom /activities-Endpunkt der ORCID-API.
        n: Die Zahl der Publikationen, die nach DOI durchsucht werden soll. Wenn alle durchsucht werden sollen, übergib
        float("inf") als Argument.

    Returns:
        Extrahierte DOI's als Liste aus Strings.
    """

    dois = []

    publications = orcid_data.get("works", {}).get("group", [])

    for i, work in enumerate(publications):
        if i == n:
            break

        ids = work.get("external-ids", {}).get("external-id", [])

        current_doi = ""

        for id in ids:
            if id.get("external-id-type", "") == "doi":
                current_doi = id.get("external-id-value", "")

        if current_doi:
            dois.append(current_doi)
        else:
            pass

    return dois
