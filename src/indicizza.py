import json
import time
from pypdf import PdfReader
from chunking import spezza_testo
from embeddings import crea_embedding

# --- 1. Leggo e spezzo il PDF ---
print("Leggo il PDF...")
lettore = PdfReader("documenti/lancer.pdf")
testo_completo = ""
for pagina in lettore.pages:
    testo_completo += pagina.extract_text()

pezzi = spezza_testo(testo_completo, dimensione=1000)
print(f"Manuale spezzato in {len(pezzi)} pezzi\n")

# --- 2. Calcolo gli embedding (lento, ma una volta sola) ---
print("Calcolo gli embedding... (pazienta, ci vuole qualche minuto)")
inizio_totale = time.time()          # segno l'ora di partenza

indice = []
for i, pezzo in enumerate(pezzi):
    t0 = time.time()                 # ora prima di questo embedding
    embedding = crea_embedding(pezzo)
    dt = time.time() - t0            # quanto è durato questo singolo embedding

    indice.append({"testo": pezzo, "embedding": embedding})
    if i % 20 == 0:
        print(f"  ...{i}/{len(pezzi)}  (ultimo pezzo: {dt:.2f}s)")

durata = time.time() - inizio_totale   # tempo totale
print(f"\nEmbedding completati in {durata:.1f} secondi ({durata/60:.1f} minuti)")

# --- 3. Salvo tutto su disco ---
with open("indice.json", "w", encoding="utf-8") as f:
    json.dump(indice, f)

print(f"Salvati {len(indice)} pezzi in indice.json")