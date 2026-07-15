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

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
