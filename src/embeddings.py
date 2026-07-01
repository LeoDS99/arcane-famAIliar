import httpx


def crea_embedding(testo):
    risposta = httpx.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": testo},
        timeout= 60
    )
    return risposta.json()["embedding"]


def somiglianza(a, b):
    # Misura quanto due embedding sono "vicini" (1 = identici, 0 = scorrelati)
    prodotto = sum(x * y for x, y in zip(a, b))
    norma_a = sum(x * x for x in a) ** 0.5
    norma_b = sum(y * y for y in b) ** 0.5
    return prodotto / (norma_a * norma_b)

if __name__ == "__main__":
    # Tre frasi: le prime due simili, la terza diversa
    frase1 = "Un fucile al plasma infligge molti danni"
    frase2 = "L'arma a energia causa gravi ferite"
    frase3 = "La ricetta della carbonara richiede uova e guanciale"

    emb1 = crea_embedding(frase1)
    emb2 = crea_embedding(frase2)
    emb3 = crea_embedding(frase3)

    print(f"Frase 1 vs Frase 2 (simili):  {somiglianza(emb1, emb2):.3f}")
    print(f"Frase 1 vs Frase 3 (diverse): {somiglianza(emb1, emb3):.3f}")