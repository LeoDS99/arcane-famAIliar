

def spezza_testo(testo, dimensione = 1000):
    chunk = []                               # la lista dove metto i pezzi
    inizio = 0
    
    while inizio < len(testo):
        fine = inizio + dimensione       # dove finisce questo pezzo
        pezzo = testo[inizio:fine]       # ritaglio da 'inizio' a 'fine'
        chunk.append(pezzo)       # aggiungo il pezzo alla lista
        inizio = fine               # sposto l'inizio al pezzo successivo
        
        
    return chunk
    
    
    # --- Prova con un testo finto corto (dimensione piccola per vedere l'effetto) ---
# --- Ora sul PDF vero ---
from pypdf import PdfReader

# Estraggo tutto il testo del manuale (come in leggi_pdf.py)
lettore = PdfReader("documenti/lancer.pdf")
testo_completo = ""
for pagina in lettore.pages:
    testo_completo += pagina.extract_text()

# Lo spezzo in pezzi da 1000 caratteri
pezzi = spezza_testo(testo_completo, dimensione=1000)

print(f"Il manuale è stato spezzato in {len(pezzi)} pezzi\n")

# Sbircio un pezzo a caso in mezzo al manuale, per vedere com'è fatto
print("--- Esempio, pezzo n.50 ---")
print(pezzi[50])