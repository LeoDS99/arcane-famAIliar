"""Interfacce dei provider di modelli (embedding e generazione).

Definiscono il contratto che ogni provider concreto deve rispettare,
così il resto del codice dipende dall'interfaccia e non da un fornitore
specifico (Ollama, un fake per i test, ecc.).
"""
import hashlib
from random import Random
from typing import Protocol

import httpx

from src.config import OLLAMA_HOST


class EmbeddingProvider(Protocol):
    """Contratto per un fornitore di embedding.

    Qualsiasi oggetto con un metodo crea_embedding con questa firma
    è un EmbeddingProvider valido, senza bisogno di ereditarietà
    esplicita (structural typing).
    """

    def crea_embedding(self, testo: str) -> list[float]:
        """Trasforma un testo nel suo vettore di embedding."""
        ...
        
        
class OllamaEmbedding:
    """Provider di embedding basato su Ollama, in locale.

    Implementa EmbeddingProvider chiamando l'API /api/embeddings di
    un'istanza Ollama in esecuzione sulla macchina.
    """

    def __init__(self, modello: str = "nomic-embed-text", host: str = OLLAMA_HOST):
        self.modello = modello
        self.host = host

    def crea_embedding(self, testo: str) -> list[float]:
        risposta = httpx.post(
            f"{self.host}/api/embeddings",
            json={"model": self.modello, "prompt": testo},
            timeout=60,
        )
        return risposta.json()["embedding"]
    

class FakeEmbedding:
    """Provider di embedding finto e deterministico, per i test.

    Non chiama nessun modello: deriva un vettore riproducibile dal
    testo, così lo stesso testo produce sempre lo stesso vettore
    (come un vero embedding), ma testi diversi producono vettori
    diversi. Serve a testare la logica di retrieval senza dipendere
    da Ollama.
    """

    def __init__(self, dimensione: int = 768):
        self.dimensione = dimensione

    def crea_embedding(self, testo: str) -> list[float]:
        # L'hash del testo è stabile: lo stesso testo dà sempre lo
        # stesso seme, quindi lo stesso vettore.
        seme = int(hashlib.sha256(testo.encode("utf-8")).hexdigest(), 16)
        generatore = Random(seme)
        return [generatore.uniform(-1, 1) for _ in range(self.dimensione)]