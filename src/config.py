"""Configurazione centrale letta dall'ambiente."""
import os

# Indirizzo base del server Ollama.
# In locale è localhost; nel container Docker si passa host.docker.internal
# tramite la variabile d'ambiente OLLAMA_HOST.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")