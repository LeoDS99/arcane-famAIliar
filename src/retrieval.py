from pypdf import PdfReader
from chunking import spezza_testo
from embeddings import crea_embedding, somiglianza

# --- 1. Leggo il PDF e lo spezzo ---
print("Leggo il PDF...")
lettore = PdfReader("documenti/lancer.pdf")
testo_completo = ""
for pagina in lettore.pages:
    testo_completo += pagina.extract_text()

pezzi = spezza_testo(testo_completo, dimensione=1000)
print(f"Manuale spezzato in {len(pezzi)} pezzi\n")

# --- 2. Trasformo OGNI pezzo in embedding (lento: ~qualche minuto) ---
print("Creo gli embedding dei pezzi... (pazienta, ci vuole un po')")
embedding_pezzi = []
for i, pezzo in enumerate(pezzi):
    embedding_pezzi.append(crea_embedding(pezzo))
    if i % 20 == 0:                 # ogni 20, stampo a che punto sono
        print(f"  ...{i}/{len(pezzi)}")
print("Embedding completati!\n")

# --- 3. La domanda ---
domanda = "Quanti punti struttura ha un mech?"
emb_domanda = crea_embedding(domanda)

# --- 4. Confronto la domanda con ogni pezzo e trovo i migliori ---
punteggi = []
for i, emb in enumerate(embedding_pezzi):
    score = somiglianza(emb_domanda, emb)
    punteggi.append((score, i))

punteggi.sort(reverse=True)                # ordino dal più vicino al più lontano

# --- 5. Mostro i 3 pezzi più rilevanti ---
print(f"Domanda: {domanda}\n")
print("=== I 3 pezzi più rilevanti ===\n")
for score, i in punteggi[:3]:
    print(f"[somiglianza {score:.3f}]")
    print(pezzi[i][:300])
    print("---\n")