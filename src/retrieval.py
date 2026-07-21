"""Ricerca semantica sull'indice: data una domanda, trova i pezzi più rilevanti del manuale."""
import json
import os
import httpx
from src.embeddings import crea_embedding, somiglianza
from src.config import OLLAMA_HOST

def carica_indice(percorso):
    """Carica un indice di embedding da disco.

    Se il file non esiste (documento non ancora indicizzato), restituisce
    una lista vuota invece di sollevare un'eccezione.

    Args:
        percorso: percorso del file JSON dell'indice da caricare.

    Returns:
        La lista dei pezzi indicizzati, o una lista vuota se il file manca.
    """
    if not os.path.exists(percorso):
        return []
    with open(percorso, "r", encoding="utf-8") as f:
        return json.load(f)
    """Carica l'indice degli embedding da disco.

    Se il file non esiste ancora (es. nessun PDF è stato indicizzato),
    restituisce una lista vuota invece di sollevare un'eccezione, così
    l'applicazione può avviarsi comunque.

    Args:
        percorso: percorso del file JSON dell'indice.

    Returns:
        La lista dei pezzi indicizzati, o una lista vuota se il file manca.
    """
    if not os.path.exists(percorso):
        return []
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
    prompt = f"""Sei un assistente che risponde a domande su un documento fornito dall'utente.

Istruzioni:
- Rispondi usando ESCLUSIVAMENTE le informazioni presenti nel CONTESTO qui sotto.
- Concentrati sulla DOMANDA dell'utente: estrai e sintetizza le informazioni pertinenti, ignorando i dettagli non attinenti anche se presenti nel contesto.
- Se la domanda chiede la definizione o la spiegazione di un concetto, forniscila in modo chiaro e diretto.
- Se il contesto non contiene abbastanza informazioni per rispondere, dillo onestamente senza inventare.
- Rispondi nella stessa lingua della domanda.

CONTESTO:
{contesto}

DOMANDA: {domanda}

RISPOSTA:"""

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

def rispondi_stream(domanda, indice):
    """Genera la risposta in streaming, cedendo i frammenti man mano.

    Come rispondi(), ma invece di attendere la risposta completa la
    trasmette pezzo per pezzo (token per token) sfruttando lo streaming
    nativo di Ollama. Utile per mostrare la risposta parola per parola.

    Args:
        domanda: la domanda dell'utente.
        indice: l'indice degli embedding su cui cercare.

   Yields:
        Tuple (tipo, dato): prima ("fonti", lista dei pezzi usati),
        poi ("frammento", testo) per ogni pezzo di risposta generato.
    """
    risultati = cerca(domanda, indice)
    contesto = "\n\n".join(testo for _, testo in risultati)

    # Prima di generare, comunico da quali pezzi del documento nasce la risposta.
    fonti = [
        {"punteggio": round(score, 4), "testo": testo}
        for score, testo in risultati
    ]
    yield ("fonti", fonti)

    prompt = f"""Sei un assistente che risponde a domande su un documento fornito dall'utente.

Istruzioni:
- Rispondi usando ESCLUSIVAMENTE le informazioni presenti nel CONTESTO qui sotto.
- Concentrati sulla DOMANDA dell'utente: estrai e sintetizza le informazioni pertinenti, ignorando i dettagli non attinenti anche se presenti nel contesto.
- Se la domanda chiede la definizione o la spiegazione di un concetto, forniscila in modo chiaro e diretto.
- Se il contesto non contiene abbastanza informazioni per rispondere, dillo onestamente senza inventare.
- Rispondi nella stessa lingua della domanda.

CONTESTO:
{contesto}

DOMANDA: {domanda}

RISPOSTA:"""

    with httpx.stream(
        "POST",
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        },
        timeout=120,
    ) as risposta:
        for riga in risposta.iter_lines():
            if not riga:
                continue
            dato = json.loads(riga)
            frammento = dato.get("message", {}).get("content", "")
            if frammento:
                yield ("frammento", frammento)

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
