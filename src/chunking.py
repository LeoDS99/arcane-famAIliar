

def spezza_testo(testo, dimensione = 1000):
    chunk = []                               # la lista dove metto i pezzi
    inizio = 0
    
    while inizio < len(testo):
        fine = inizio + dimensione       # dove finisce questo pezzo
        pezzo = testo[inizio:fine]       # ritaglio da 'inizio' a 'fine'
        chunk.append(pezzo)       # aggiungo il pezzo alla lista
        inizio = fine               # sposto l'inizio al pezzo successivo
        
        
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