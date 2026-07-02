"""Ricerca semantica sull'indice: data una domanda, trova i pezzi più rilevanti del manuale."""
import json
from embeddings import crea_embedding, somiglianza


def carica_indice(percorso="indice.json"):
    with open(percorso, "r", encoding="utf-8") as f:
        return json.load(f)
    
def cerca(domanda, indice, quanti=3):
    #trasforma la domanda in embdedding
    emd_domanda = crea_embedding(domanda)
    
    #Confronto la domanda in embedding
    punteggi = []
    for pezzo in indice:
        score = somiglianza(emd_domanda, pezzo["embedding"])
        punteggi.append((score, pezzo["testo"]))
        
    #Ordino dal più vicino al più lontano e tengo i primi 'quanti'
    punteggi.sort(reverse=True, key=lambda x: x[0])
    return punteggi[:quanti]

if __name__ == "__main__":
    print("Carico l'indice...")
    indice = carica_indice()
    print(f"Pronti! {len(indice)} pezzi caricati.\n")

    domanda = "Quanti punti struttura ha un mech?"
    print(f"Domanda: {domanda}\n")

    risultati = cerca(domanda, indice)

    print("=== Pezzi più rilevanti ===\n")
    for score, testo in risultati:
        print(f"[somiglianza {score:.3f}]")
        print(testo[:300])
        print("---\n")