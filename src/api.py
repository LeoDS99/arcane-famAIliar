"""API web che espone l'assistente RAG via HTTP."""
from fastapi import FastAPI
from pydantic import BaseModel
from src.retrieval import carica_indice, rispondi

app = FastAPI()

print(">>> Carico l'indice...")
indice = carica_indice()
print(f">>> Pronti! {len(indice)} pezzi caricati.")


class Domanda(BaseModel):
    testo: str


@app.post("/chiedi")
def chiedi(domanda: Domanda):
    risposta = rispondi(domanda.testo, indice)
    return {"risposta": risposta}