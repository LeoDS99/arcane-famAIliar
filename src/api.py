"""API web che espone l'assistente RAG via HTTP."""
import json
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.retrieval import carica_indice, rispondi, rispondi_stream
from src.indicizza import indicizza_pdf, indicizza_pdf_stream
from src.documenti import elenca_documenti, percorso_indice


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CARTELLA_UPLOAD = Path("uploads")

# Documento attualmente attivo e il suo indice in memoria.
# All'avvio nessun documento è attivo: l'utente ne sceglie uno.
stato = {"documento": None, "indice": []}
print(">>> Backend pronto. Nessun documento attivo.")

class Domanda(BaseModel):
    testo: str


@app.post("/chiedi")
def chiedi(domanda: Domanda):
    """Risponde a una domanda basandosi sull'indice caricato.

    Args:
        domanda: la domanda dell'utente.

    Raises:
        HTTPException: 400 se la domanda è vuota.

    Returns:
        La risposta generata dal modello.
    """
    if not domanda.testo.strip():
        raise HTTPException(status_code=400, detail="La domanda non può essere vuota.")

    risposta = rispondi(domanda.testo, stato["indice"])
    return {"risposta": risposta}

@app.get("/chiedi-stream")
def chiedi_stream(domanda: str):
    """Risponde a una domanda trasmettendo la risposta via SSE.

    A differenza di /chiedi, che risponde in blocco, questo endpoint
    trasmette la risposta frammento per frammento man mano che il
    modello la genera, per mostrarla parola per parola.

   Args:
        domanda: la domanda dell'utente.

    Raises:
        HTTPException: 400 se la domanda è vuota.

    Returns:
        Uno stream SSE: prima le fonti usate, poi i frammenti di risposta.
    """
    if not domanda.strip():
        raise HTTPException(status_code=400, detail="La domanda non può essere vuota.")
    
    def genera_eventi():
        for tipo, dato in rispondi_stream(domanda, stato["indice"]):
            yield f"data: {json.dumps({tipo: dato})}\n\n"

        yield f"data: {json.dumps({'completato': True})}\n\n"

    return StreamingResponse(genera_eventi(), media_type="text/event-stream")


@app.get("/stato")
def stato_indice():
    """Indica quale documento è attivo e con quanti pezzi.

    Returns:
        Il documento attivo (o None), un flag di presenza e i pezzi.
    """
    numero_pezzi = len(stato["indice"])
    return {
        "documento": stato["documento"],
        "indice_presente": numero_pezzi > 0,
        "pezzi": numero_pezzi,
    }
    
@app.get("/documenti")
def documenti():
    """Elenca i PDF caricati e se ciascuno è già indicizzato.

    Returns:
        La lista dei documenti nella libreria.
    """
    return {"documenti": elenca_documenti()}
    
    
@app.post("/attiva")
def attiva(nome: str):
    """Rende attivo un documento già indicizzato, senza re-indicizzare.

    Carica in memoria l'indice del documento indicato, così le domande
    successive vengono risposte basandosi su di esso.

    Args:
        nome: nome del PDF da attivare (deve essere già indicizzato).

    Raises:
        HTTPException: 404 se il documento non ha un indice.

    Returns:
        Il documento attivato e il numero di pezzi caricati.
    """
    destinazione = percorso_indice(nome)
    if not destinazione.exists():
        raise HTTPException(
            status_code=404,
            detail="Documento non indicizzato.",
        )

    stato["documento"] = nome
    stato["indice"] = carica_indice(str(destinazione))
    return {
        "documento": nome,
        "pezzi": len(stato["indice"]),
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
    """Riceve un PDF, ne verifica la validità e lo salva su disco.

    Il file viene accettato solo se è un vero PDF (controllo sulla firma
    dei primi byte, non solo sull'estensione). L'indicizzazione avviene
    poi tramite l'endpoint /indicizza-stream.

    Args:
        file: il PDF caricato dall'utente.

    Raises:
        HTTPException: 400 se il file non è un PDF valido.

    Returns:
        Il nome del file salvato.
    """
    contenuto = await file.read()

    # Un PDF valido inizia sempre con la firma "%PDF".
    if not contenuto.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Il file caricato non è un PDF valido.",
        )

    CARTELLA_UPLOAD.mkdir(exist_ok=True)
    percorso = CARTELLA_UPLOAD / file.filename
    percorso.write_bytes(contenuto)

    return {"nome": file.filename}
@app.get("/indicizza-stream")
def indicizza_stream(nome: str):
    """Indicizza un PDF già caricato, trasmettendo il progresso via SSE.

    L'indice viene salvato in indici/<nome>.json e il documento diventa
    quello attivo. Per ogni pezzo invia un evento di avanzamento; al
    termine invia un evento finale.

    Args:
        nome: nome del file (già salvato in CARTELLA_UPLOAD) da indicizzare.

    Returns:
        Uno stream di eventi Server-Sent Events.
    """
    percorso_pdf = CARTELLA_UPLOAD / nome
    destinazione = str(percorso_indice(nome))

    def genera_eventi():
        for fatti, totale in indicizza_pdf_stream(str(percorso_pdf), destinazione):
            dati = json.dumps({"fatti": fatti, "totale": totale})
            yield f"data: {dati}\n\n"

        # Il documento appena indicizzato diventa quello attivo.
        stato["documento"] = nome
        stato["indice"] = carica_indice(destinazione)
        finale = json.dumps({"completato": True, "pezzi": len(stato["indice"])})
        yield f"data: {finale}\n\n"

    return StreamingResponse(genera_eventi(), media_type="text/event-stream")