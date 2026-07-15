import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "vektor"
DATA_DIR = Path.home() / ".config" / APP_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_PATH = DATA_DIR / "vektor.db"
CHROMA_PATH = DATA_DIR / "chroma_db"
WORKSPACE_DIR = DATA_DIR / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "mistralai/mistral-nemo")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
