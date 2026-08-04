"""Test unitari della logica di cerca(): ordinamento e taglio top-k.

A differenza di test_retrieval.py (che verifica la qualità semantica del
retrieval reale con Ollama), qui si testa solo la meccanica di cerca()
usando un provider fake e deterministico. Nessun modello, nessun indice
su disco: gira ovunque, anche in CI.
"""
from src.providers import FakeEmbedding
from src.retrieval import cerca


def costruisci_indice(provider, testi):
    """Costruisce un indice nel formato atteso da cerca(), dai testi dati."""
    return [
        {"testo": testo, "embedding": provider.crea_embedding(testo)}
        for testo in testi
    ]


def test_cerca_mette_per_primo_il_chunk_identico_alla_domanda():
    """Un chunk con lo stesso testo della domanda ha similarità 1.0,
    quindi deve risultare primo."""
    provider = FakeEmbedding()
    domanda = "cosa è un impulso"
    indice = costruisci_indice(
        provider,
        ["un testo qualunque", domanda, "un altro testo diverso"],
    )

    risultati = cerca(domanda, indice, provider, quanti=3)

    # Il primo risultato deve essere il chunk identico alla domanda.
    primo_testo = risultati[0][1]
    assert primo_testo == domanda


def test_cerca_rispetta_il_limite_top_k():
    """cerca() non deve restituire più di 'quanti' risultati."""
    provider = FakeEmbedding()
    indice = costruisci_indice(
        provider,
        ["testo uno", "testo due", "testo tre", "testo quattro", "testo cinque"],
    )

    risultati = cerca("una domanda", indice, provider, quanti=2)

    assert len(risultati) == 2