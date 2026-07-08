import json
import logging

from pypdf import PdfReader

from src.chunking import spezza_testo
from src.embeddings import crea_embedding

# Dimensione (in caratteri) di ogni pezzo in cui viene spezzato il testo.
DIMENSIONE_CHUNK = 1000
# File su cui viene salvato l'indice degli embedding.
PERCORSO_INDICE = "indice.json"


logger = logging.getLogger(__name__)


def indicizza_pdf_stream(percorso_pdf: str):
    """Indicizza un PDF cedendo il progresso pezzo per pezzo.

    È un generator: per ogni chunk elaborato cede una tupla
    (fatti, totale), utile per mostrare una barra di avanzamento.
    Al termine salva l'indice completo su disco.

    Args:
        percorso_pdf: percorso del file PDF da indicizzare.

    Yields:
        Tuple (fatti, totale) man mano che i pezzi vengono elaborati.
    """
    logger.info("Inizio indicizzazione di %s", percorso_pdf)

    lettore = PdfReader(percorso_pdf)
    testo_completo = ""
    for pagina in lettore.pages:
        testo_completo += pagina.extract_text() or ""

    pezzi = spezza_testo(testo_completo, dimensione=DIMENSIONE_CHUNK)
    totale = len(pezzi)

    indice = []
    for i, pezzo in enumerate(pezzi):
        embedding = crea_embedding(pezzo)
        indice.append({"testo": pezzo, "embedding": embedding})
        yield (i + 1, totale)

    with open(PERCORSO_INDICE, "w", encoding="utf-8") as f:
        json.dump(indice, f)

    logger.info("Indicizzazione completata: %d pezzi salvati", len(indice))


def indicizza_pdf(percorso_pdf: str) -> int:
    """Indicizza un PDF e restituisce il numero di pezzi indicizzati.

    Wrapper sincrono attorno a indicizza_pdf_stream: consuma tutto il
    generator (eseguendo l'indicizzazione) e ne ricava il totale.
    Adatto a chi non ha bisogno del progresso (es. la CLI).

    Args:
        percorso_pdf: percorso del file PDF da indicizzare.

    Returns:
        Il numero di pezzi indicizzati.
    """
    totale = 0
    for _, totale in indicizza_pdf_stream(percorso_pdf):
        pass
    return totale


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    numero_pezzi = indicizza_pdf("documenti/lancer.pdf")
    print(f"Indicizzati {numero_pezzi} pezzi in {PERCORSO_INDICE}")