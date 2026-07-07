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


def indicizza_pdf(percorso_pdf: str) -> int:
    """Legge un PDF, ne calcola gli embedding e salva l'indice su disco.

    Il PDF viene spezzato in pezzi di DIMENSIONE_CHUNK caratteri e per
    ognuno viene calcolato l'embedding. Il risultato sostituisce il
    contenuto di PERCORSO_INDICE.

    Args:
        percorso_pdf: percorso del file PDF da indicizzare.

    Returns:
        Il numero di pezzi indicizzati.
    """
    logger.info("Inizio indicizzazione di %s", percorso_pdf)

    lettore = PdfReader(percorso_pdf)
    testo_completo = ""
    for pagina in lettore.pages:
        testo_completo += pagina.extract_text() or ""

    pezzi = spezza_testo(testo_completo, dimensione=DIMENSIONE_CHUNK)

    indice = []
    for pezzo in pezzi:
        embedding = crea_embedding(pezzo)
        indice.append({"testo": pezzo, "embedding": embedding})

    with open(PERCORSO_INDICE, "w", encoding="utf-8") as f:
        json.dump(indice, f)

    logger.info("Indicizzazione completata: %d pezzi salvati", len(indice))
    return len(indice)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    numero_pezzi = indicizza_pdf("documenti/lancer.pdf")
    print(f"Indicizzati {numero_pezzi} pezzi in {PERCORSO_INDICE}")