"""Unit test della funzione di chunking. Puri: nessuna dipendenza esterna."""
import pytest

from src.chunking import spezza_testo


def test_overlap_ripete_la_coda_del_pezzo_precedente():
    """Ogni pezzo deve ripetere gli ultimi 'sovrapposizione' caratteri."""
    risultato = spezza_testo("ABCDEFGHIJ", dimensione=4, sovrapposizione=2)
    assert risultato == ["ABCD", "CDEF", "EFGH", "GHIJ"]


def test_nessun_pezzo_ridondante_in_coda():
    """L'ultimo pezzo non deve essere un mozzicone già contenuto altrove."""
    risultato = spezza_testo("ABCDEFGHIJ", dimensione=4, sovrapposizione=2)
    assert risultato[-1] == "GHIJ"


def test_senza_sovrapposizione_taglia_netto():
    """Con sovrapposizione=0 i pezzi sono affiancati senza ripetizioni."""
    risultato = spezza_testo("ABCDEF", dimensione=3, sovrapposizione=0)
    assert risultato == ["ABC", "DEF"]


def test_sovrapposizione_troppo_grande_solleva_errore():
    """sovrapposizione >= dimensione deve sollevare ValueError."""
    with pytest.raises(ValueError):
        spezza_testo("ciao", dimensione=100, sovrapposizione=100)