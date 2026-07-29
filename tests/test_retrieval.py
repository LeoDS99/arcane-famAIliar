"""Eval suite del retrieval: verifica che le domande del golden set
recuperino i pezzi di documento attesi."""
import json
from pathlib import Path

import pytest

from src.retrieval import carica_indice, cerca

RADICE = Path(__file__).resolve().parent.parent
PERCORSO_GOLDEN_SET = Path(__file__).resolve().parent / "golden_set.json"
CARTELLA_INDICI = RADICE / "indici"


def carica_golden_set():
    """Legge i casi di test dal golden set su disco."""
    with open(PERCORSO_GOLDEN_SET, "r", encoding="utf-8") as f:
        return json.load(f)


CASI = carica_golden_set()

def _parametro(caso):
    """Trasforma un caso del golden set in un parametro pytest.

    I casi con la chiave 'xfail' sono fallimenti noti del retrieval: vengono
    marcati come attesi-in-errore in modalità strict, così la suite segnala
    anche il caso opposto, cioè quando tornano a passare da soli.
    """
    motivo = caso.get("xfail")
    marks = [pytest.mark.xfail(reason=motivo, strict=True)] if motivo else []
    return pytest.param(caso, id=caso["domanda"], marks=marks)


CASI_PARAMETRIZZATI = [_parametro(caso) for caso in CASI]

@pytest.mark.parametrize("caso", CASI_PARAMETRIZZATI)
def test_retrieval_trova_il_pezzo_atteso(caso):
    """Il pezzo atteso deve comparire tra i risultati restituiti da cerca()."""
    indice = carica_indice(CARTELLA_INDICI / f"{caso['documento']}.json")
    assert indice, f"Indice vuoto o mancante per '{caso['documento']}'"

    risultati = cerca(caso["domanda"], indice)
    testi = [testo for _, testo in risultati]

    assert any(caso["chunk_atteso_contiene"] in testo for testo in testi), (
        f"'{caso['chunk_atteso_contiene']}' non trovato nei risultati "
        f"per la domanda: {caso['domanda']}"
    )