import json
import requests
import logging

logger = logging.getLogger(__name__)

def triple_to_nl_sentence(tripel: tuple[str, str, str],
                          model: str="llama-3.2-3b-instruct",
                          url: str="http://localhost:1234/v1/completions"
                         ) -> str:

    prompt = f"""
    Konstruiere aus diesen drei Token einen deutschen Satz, der ein Arbeitsverhältnis beschreibt:
    Die Token sind immer in dieser Reihenfolge: Funktion, Abteilung, Organisation und sie sollen nach diesem Muster geordnet werden:
    Muster: Token1 [am|bei|von|in der|(...)] Token2 [an der|am|(...)] Token3$
    
    Beachte dabei immer diese Regeln:
    
    1. Die Bindewörter in den eckigen Klammern kannst du an den Kontext anpassen. Nutze immer deutsche Wörter für die Bindewörter in den eckigen Klammern.
    2. Übersetze die Token im Ergebnissatz nicht.
    
    Hinweise: Die eckigen Klammern enthalten einige Bindewörter als Beispiele, die häufig sinnvoll sind.
    
    Beispiele:
    Token: 'Professor', 'Institut für Medienwissenschaft', 'Philipps-Universität Marburg'
    Muster: Token1 [am|bei|von|in der|(...)] Token2 [an der|am|(...)] Token3$
    Satz: Professor am Institut für Medienwissenschaft an der Philipps-Universität Marburg
    
    Token: 'Executive Director', 'Marburg Center for Digital Culture and Infrastructure', 'Philipps Universität Marburg'
    Muster: Token1 [am|bei|von|in der|(...)] Token2 [an der|am|(...)] Token3$
    Satz: Executive Director des Marburg Center for Digital Culture and Infrastructure an der Philipps-Universität Marburg
    
    Token: 'Wissenschaftlicher Mitarbeiter', 'Abteilung für Forschungsinfrastruktur', 'Herder Institut'
    Muster: Token1 [am|bei|von|in der|(...)] Token2 [an der|am|(...)] Token3$
    Satz: Wissenschaftlicher Mitarbeiter in der Abteilung für Forschungsinfrastruktur am Herder Institut
    
    Token: 'Chair International History', 'History', 'Universität Trier'
    Muster: Token1 [am|bei|von|in der|(...)] Token2 [an der|am|(...)] Token3$
    Satz: Chair International History am Institut für History an der Universität Trier
    
    Token: {tripel[0]}, {tripel[1]}, {tripel[2]}
    Muster: Token1 [am|bei|von|in der] Token2 [an der/am] Token3$
    Satz: 
    
    Gib nur einen korrekten Satz zurück, der das letzte Beispiel ergänzt ohne Erklärung und ohne mit einem Punkt zu enden.
    """


    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "temperature": 0.1,
        "max_tokens": 100
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        text = response.json().get("choices", "")[0].get("text", "").strip()
        index = text.find("\n")

        logger.info(f"Das Tripel {tripel} wurde zum folgenden natürlichsprachigen Satz transformiert:\n"
                    f"{text[:index]}")

        return text[:index]
    except requests.exceptions.RequestException:
        logger.warning(f"Stelle sich, dass lmmanager auf deinem Rechner läuft und {model} unter"
                     f"{url} erreichbar ist.\n"
                     "Das unformatierte Tripel wird zurückgegeben.")

        return " ".join(tripel) if not any(e is None for e in tripel) else ""
