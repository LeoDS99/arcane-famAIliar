import json
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
indice = []   # qui metto coppie {testo del pezzo, suo embedding}
for i, pezzo in enumerate(pezzi):
    embedding = crea_embedding(pezzo)
    indice.append({"testo": pezzo, "embedding": embedding})
    if i % 20 == 0:
        print(f"  ...{i}/{len(pezzi)}")

# --- 3. Salvo tutto su disco ---
with open("indice.json", "w", encoding="utf-8") as f:
    json.dump(indice, f)

print(f"\nFatto! Salvati {len(indice)} pezzi in indice.json")