"""API web che espone l'assistente RAG via HTTP."""
from fastapi import FastAPI
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