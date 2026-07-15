from pathlib import Path

APP_NAME = "vektor"
DATA_DIR = Path.home() / ".config" / APP_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_PATH = DATA_DIR / "vektor.db"
CHROMA_PATH = DATA_DIR / "chroma_db"

OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_HOST = "http://localhost:11434"
