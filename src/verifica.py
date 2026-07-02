"""Controlla la salute dell'indice: verifica che ogni pezzo abbia un embedding valido."""
import json

DIMENSIONE_ATTESA = 768   # nomic-embed-text produce vettori da 768 numeri


def controlla_indice(percorso="indice.json"):
    with open(percorso, "r", encoding="utf-8") as f:
        indice = json.load(f)

    print(f"L'indice contiene {len(indice)} pezzi")

    rotti = 0
    for i, pezzo in enumerate(indice):
        lunghezza = len(pezzo["embedding"])
        if lunghezza != DIMENSIONE_ATTESA:
            print(f"  Pezzo {i}: embedding anomalo ({lunghezza} numeri)")
            rotti += 1

    if rotti == 0:
        print(f"Tutti i pezzi hanno un embedding valido da {DIMENSIONE_ATTESA} numeri.")
    else:
        print(f"Attenzione: {rotti} pezzi con embedding non valido.")


if __name__ == "__main__":
    controlla_indice()