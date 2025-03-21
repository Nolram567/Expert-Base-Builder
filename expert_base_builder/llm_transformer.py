"""
Wird derzeit nicht genutzt. Die letzte Version wurde nicht auf Fehler überprüft.
"""

import json
from typing import List
import prompts
import requests
import logging

logger = logging.getLogger(__name__)

def triple_to_nl_sentence(tripel: tuple[str, str, str],
                          model: str="llama-3.2-3b-instruct",
                          url: str="http://localhost:1234/v1/completions"
                         ) -> str:

    exit_code = check_triple(tripel)

    prompt = pick_prompt(exit_code)

    if type(exit_code) == list:
        if exit_code in [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            logger.warning(f"Das Tupel {tripel} hat nur einen gültigen Wert. Gebe Wert zurück.")
            return " ".join(tripel) if not any(e is None for e in tripel) else ""
        else:
            prompt = pick_prompt(exit_code).format(tripel[0], tripel[2])
    elif exit_code == 0:
        prompt = prompts.prompt111.format(tripel[0], tripel[1], tripel[2])
    elif exit_code < 0:
        logger.warning(f"Das Tupel {tripel} ist ungültig. Gebe unformatiertes Tupel zurück.")
        return " ".join(tripel) if not any(e is None for e in tripel) else ""

    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "temperature": 0.1,
        "max_tokens": 100
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        print(json.dumps(response.json(), indent=4))
        text = response.json().get("choices", "")[0].get("text", "").strip()
        index = text.find("\n")

        logger.info(f"Das Tripel {tripel} wurde zum folgenden natürlichsprachigen Satz transformiert:\n"
                    f"{text[:index]}")

        return text[:index]
    except requests.exceptions.RequestException:
        logger.warning(f"Stelle sich, dass lm studio auf deinem Rechner läuft und {model} unter"
                     f"{url} erreichbar ist.\n"
                     "Das unformatierte Tripel wird zurückgegeben.")

        return " ".join(tripel) if not any(e is None for e in tripel) else ""

def check_triple(tripel: tuple[str,str,str]) -> int or List[int]:
    """
    Diese Funktion checkt ein Tripel auf Gültigkeit. Das Ergebnis wird als integer oder als Liste aus Integern zurückgegeben.
    Dabei bedeutet:
    -2: Das übergebene Tupel ist kein Tripel.
    -1: Das Tripel besteht nur aus Werten, die zu False evaluieren, wie None oder Nullstrings.
     0: Das Tripel ist gültig.
    [x,y,z]: Das Tripel ist gültig, enthält aber mindestens einen Wert, der zu False evaluiert;
            Beispiel: ["String", None, "String"] → [1,0,1]

    Args:
        tripel: Das zu überprüfende Tripel.
    Returns:
        Ein Exit Code oder eine Liste aus ganzen Zahlen.
    """
    if not len(tripel) == 3:
        return -2

    if any(tripel):
        if all(tripel):
            return 0
        else:
            return [1 if e else 0 for e in tripel]
    else:
        return -1

def pick_prompt(exit_code: list or int) -> str:
    """
    Diese Funktion wählt den passenden Prompt für ein Datentripel aus.

    Args:
        exit_code: Der Rückgabewert der Funktion check_triple(), wenn er eine Liste ist.
    """

    if exit_code == [0, 1, 1]:
        return prompts.prompt011
    elif exit_code == [1, 0, 1]:
        return prompts.prompt101
    elif exit_code == [1, 1, 0]:
        return prompts.prompt110