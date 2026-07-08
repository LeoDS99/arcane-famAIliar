"""API web che espone l'assistente RAG via HTTP."""
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.retrieval import carica_indice, rispondi
from src.indicizza import indicizza_pdf

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


@app.post("/carica")
async def carica(file: UploadFile = File(...)):
    """Riceve un PDF, lo salva su disco e ne (ri)costruisce l'indice.

    Il file caricato sostituisce l'indice esistente: da questo momento
    l'assistente risponde basandosi sul nuovo documento.

    Args:
        file: il PDF caricato dall'utente.

    Returns:
        Il nome del file e il numero di pezzi indicizzati.
    """
    CARTELLA_UPLOAD.mkdir(exist_ok=True)
    percorso = CARTELLA_UPLOAD / file.filename

    contenuto = await file.read()
    percorso.write_bytes(contenuto)

    numero_pezzi = indicizza_pdf(str(percorso))

    stato["indice"] = carica_indice()

    return {
        "nome": file.filename,
        "pezzi_indicizzati": numero_pezzi,
    }