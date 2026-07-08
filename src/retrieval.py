"""Ricerca semantica sull'indice: data una domanda, trova i pezzi più rilevanti del manuale."""
import json
from src.embeddings import crea_embedding, somiglianza
from src.config import OLLAMA_HOST
import httpx

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

def rispondi(domanda, indice):
    # 1. Trovo i pezzi rilevanti (il retrieval che già funziona)
    risultati = cerca(domanda, indice)

    # 2. Unisco i pezzi trovati in un unico blocco di "contesto"
    contesto = "\n\n".join(testo for _, testo in risultati)

    # 3. Costruisco il prompt: istruzioni + contesto + domanda
    prompt = f"""Sei un assistente esperto che risponde a domande basandosi su ciò che ti viene dato.
Rispondi alla domanda basandoti SOLO sul contesto qui sotto, tratto dal manuale.
Se il contesto non contiene la risposta, dillo onestamente.

CONTESTO:
{contesto}

DOMANDA: {domanda}"""

    # 4. Chiedo al modello di generare la risposta
    risposta = httpx.post(
      f"{OLLAMA_HOST}/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    return risposta.json()["message"]["content"]

if __name__ == "__main__":
    print("Carico l'indice...")
    indice = carica_indice()
    print("Fai una domanda sul manuale (scrivi 'esci' per uscire)\n")

    while True:
        domanda = input("Tu: ")
        if domanda == "esci":
            break

        risposta = rispondi(domanda, indice)
        print(f"\nAssistente: {risposta}\n")
