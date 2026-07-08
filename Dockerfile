# Immagine di base: Python 3.14 già installato su un Linux minimale.
FROM python:3.14-slim

# Cartella di lavoro dentro il container: da qui in poi i comandi girano qui.
WORKDIR /app

# Installo uv (il gestore che usi anche in locale) dall'immagine ufficiale.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copio prima i file delle dipendenze, da soli.
COPY pyproject.toml uv.lock ./

# Installo le dipendenze nel container.
RUN uv sync --frozen --no-dev

# Ora copio il resto del codice (la cartella src/).
COPY src/ ./src/

# Dichiaro che l'app dentro il container userà la porta 8000.
EXPOSE 8000

# Comando che parte all'avvio del container: lancia il server.
CMD ["uv", "run", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]