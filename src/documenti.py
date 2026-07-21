"""Gestione della libreria di documenti: file caricati e loro indici.

Ogni PDF in CARTELLA_UPLOAD può avere un indice corrispondente in
CARTELLA_INDICI, con lo stesso nome normalizzato ed estensione .json.
"""
import re
from pathlib import Path

from src.config import CARTELLA_UPLOAD, CARTELLA_INDICI


def normalizza_nome(nome_file: str) -> str:
    """Deriva una chiave sicura per il filesystem dal nome di un file.

    Rimuove l'estensione, mette in minuscolo e sostituisce tutto ciò che
    non è lettera o numero con un underscore. Così 'Il Mio CV (2024).pdf'
    diventa 'il_mio_cv_2024', utilizzabile come nome di file indice.

    Args:
        nome_file: il nome del file originale (es. 'Lancer.pdf').

    Returns:
        La chiave normalizzata (es. 'lancer').
    """
    senza_estensione = Path(nome_file).stem
    minuscolo = senza_estensione.lower()
    return re.sub(r"[^a-z0-9]+", "_", minuscolo).strip("_")


def percorso_indice(nome_file: str) -> Path:
    """Restituisce il percorso dell'indice associato a un PDF.

    Args:
        nome_file: il nome del PDF (es. 'Lancer.pdf').

    Returns:
        Il percorso dell'indice (es. Path('indici/lancer.json')).
    """
    chiave = normalizza_nome(nome_file)
    return Path(CARTELLA_INDICI) / f"{chiave}.json"


def elenca_documenti() -> list[dict]:
    """Elenca i PDF caricati e indica se ciascuno è già indicizzato.

    Returns:
        Una lista di dizionari, uno per PDF, con nome e stato di
        indicizzazione.
    """
    cartella = Path(CARTELLA_UPLOAD)
    if not cartella.exists():
        return []

    documenti = []
    for pdf in sorted(cartella.glob("*.pdf")):
        documenti.append(
            {
                "nome": pdf.name,
                "indicizzato": percorso_indice(pdf.name).exists(),
            }
        )
    return documenti