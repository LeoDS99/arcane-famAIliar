"""API web che espone l'assistente RAG via HTTP."""
import json
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.retrieval import carica_indice, rispondi
from src.indicizza import indicizza_pdf, indicizza_pdf_stream

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CARTELLA_UPLOAD = Path("uploads")

print(">>> Carico l'indice...")
stato = {"indice": carica_indice()}
print(f">>> Pronti! {len(stato['indice'])} pezzi caricati.")


class Domanda(BaseModel):
    testo: str


@app.post("/chiedi")
def chiedi(domanda: Domanda):
    risposta = rispondi(domanda.testo, stato["indice"])
    return {"risposta": risposta}


@app.get("/stato")
def stato_indice():
    """Indica se un indice è già caricato e con quanti pezzi.

    Permette al frontend di sapere, all'avvio, se mostrare la modale
    di upload (nessun indice) o entrare direttamente in chat.

    Returns:
        Un flag `indice_presente` e il numero di pezzi indicizzati.
    """
    numero_pezzi = len(stato["indice"])
    return {
        "indice_presente": numero_pezzi > 0,
        "pezzi": numero_pezzi,
    }
    
    
@app.get("/debug-cerca")
def debug_cerca(domanda: str, quanti: int = 3):
    """Endpoint diagnostico: mostra i pezzi recuperati per una domanda.

    Non passa dal modello di generazione: restituisce solo i chunk che
    la ricerca semantica considera più rilevanti, con il loro punteggio.
    Utile per capire se un problema è nel retrieval o nella generazione.

    Args:
        domanda: la domanda da cercare nell'indice.
        quanti: quanti pezzi recuperare (default 3).

    Returns:
        La lista dei pezzi con punteggio e un'anteprima del testo.
    """
    from src.retrieval import cerca

    risultati = cerca(domanda, stato["indice"], quanti=quanti)

    return {
        "domanda": domanda,
        "risultati": [
            {
                "punteggio": round(score, 4),
                "anteprima": testo[:300],
            }
            for score, testo in risultati
        ],
    }

@app.post("/carica")
async def carica(file: UploadFile = File(...)):
    """Riceve un PDF e lo salva su disco, senza ancora indicizzarlo.

    L'indicizzazione vera e propria avviene tramite l'endpoint
    /indicizza-stream, che ne trasmette il progresso.

    Args:
        file: il PDF caricato dall'utente.

    Returns:
        Il nome del file salvato.
    """
    CARTELLA_UPLOAD.mkdir(exist_ok=True)
    percorso = CARTELLA_UPLOAD / file.filename

    contenuto = await file.read()
    percorso.write_bytes(contenuto)

    return {"nome": file.filename}

@app.get("/indicizza-stream")
def indicizza_stream(nome: str):
    """Indicizza un PDF già caricato, trasmettendo il progresso via SSE.

    Per ogni pezzo elaborato invia un evento con lo stato di avanzamento.
    Al termine invia un evento finale e ricarica l'indice in memoria.

    Args:
        nome: nome del file (già salvato in CARTELLA_UPLOAD) da indicizzare.

    Returns:
        Uno stream di eventi Server-Sent Events.
    """
    percorso = CARTELLA_UPLOAD / nome

    def genera_eventi():
        for fatti, totale in indicizza_pdf_stream(str(percorso)):
            dati = json.dumps({"fatti": fatti, "totale": totale})
            yield f"data: {dati}\n\n"

        stato["indice"] = carica_indice()
        finale = json.dumps({"completato": True, "pezzi": len(stato["indice"])})
        yield f"data: {finale}\n\n"

    return StreamingResponse(genera_eventi(), media_type="text/event-stream")