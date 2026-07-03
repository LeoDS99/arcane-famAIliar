"""API web che espone l'assistente RAG via HTTP."""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.retrieval import carica_indice, rispondi

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print(">>> Carico l'indice...")
indice = carica_indice()
print(f">>> Pronti! {len(indice)} pezzi caricati.")


class Domanda(BaseModel):
    testo: str


@app.post("/chiedi")
def chiedi(domanda: Domanda):
    risposta = rispondi(domanda.testo, indice)
    return {"risposta": risposta}


@app.post("/carica")
async def carica(file: UploadFile = File(...)):
    """Riceve un file dall'utente e ne restituisce i metadati.

    Per ora legge il contenuto solo per misurarne la dimensione.
    Salvataggio su disco e indicizzazione arriveranno nei passi successivi.
    """
    contenuto = await file.read()
    return {
        "nome": file.filename,
        "tipo": file.content_type,
        "dimensione_byte": len(contenuto),
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    