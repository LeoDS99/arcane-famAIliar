"""Configurazione centrale letta dall'ambiente."""
import os

# Indirizzo base del server Ollama.
# In locale è localhost; nel container Docker si passa host.docker.internal
# tramite la variabile d'ambiente OLLAMA_HOST.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Cartella dei PDF caricati dagli utenti.
CARTELLA_UPLOAD = "uploads"

# Cartella degli indici, uno per ogni PDF indicizzato.
CARTELLA_INDICI = "indici"

# Numero di pezzi più rilevanti da recuperare per ogni domanda (top-k).
# Valore di partenza: 3. Andrà tarato sui dati veri quando l'eval suite
# permetterà di misurare l'effetto di k sul retrieval.
TOP_K = 3