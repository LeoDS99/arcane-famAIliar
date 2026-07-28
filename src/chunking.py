from src.config import DIMENSIONE_CHUNK, SOVRAPPOSIZIONE

def spezza_testo(testo, dimensione=DIMENSIONE_CHUNK, sovrapposizione=SOVRAPPOSIZIONE):
    """Spezza un testo in pezzi di lunghezza fissa con sovrapposizione.

    Ogni pezzo ripete gli ultimi 'sovrapposizione' caratteri del
    precedente, così un concetto a cavallo del taglio resta intero
    in almeno uno dei due pezzi.

    Args:
        testo: il testo da spezzare.
        dimensione: lunghezza in caratteri di ogni pezzo.
        sovrapposizione: caratteri ripetuti tra un pezzo e il successivo.

    Returns:
        La lista dei pezzi di testo.

    Raises:
        ValueError: se sovrapposizione è negativa o >= dimensione.
    """
    if sovrapposizione < 0 or sovrapposizione >= dimensione:
        raise ValueError(
            "sovrapposizione deve essere tra 0 e dimensione-1, "
            f"ricevuto sovrapposizione={sovrapposizione}, dimensione={dimensione}"
        )

  
    chunk = []
    inizio = 0

    while inizio < len(testo):
        fine = inizio + dimensione
        pezzo = testo[inizio:fine]
        chunk.append(pezzo)
        if fine >= len(testo):
            break
        inizio = fine - sovrapposizione

    return chunk
    

if __name__ == "__main__":
    # --- Ora sul PDF vero ---
    from pypdf import PdfReader

    lettore = PdfReader("documenti/lancer.pdf")
    testo_completo = ""
    for pagina in lettore.pages:
        testo_completo += pagina.extract_text()

    pezzi = spezza_testo(testo_completo, dimensione=1000)
    print(f"Il manuale è stato spezzato in {len(pezzi)} pezzi\n")
    print("--- Esempio, pezzo n.50 ---")
    print(pezzi[50])