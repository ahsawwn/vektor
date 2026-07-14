# Vektor

A persistent, local AI-native assistant with semantic vector memory.

## Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- [Ollama](https://ollama.com/) running locally with a model pulled (e.g. `llama3`)

## Setup

```bash
poetry install
ollama pull llama3
```

## Usage

```bash
# Start an interactive chat session
poetry run python main.py chat

# Set a user preference
poetry run python main.py remember timezone "Asia/Karachi"

# Clear all logs, preferences, and vector indexes
poetry run python main.py forget --all

# Show system status
poetry run python main.py status
```

### Chat Commands

- `/exit` or `/quit` — Exit the session
- `/clear` — Clear conversation history and vector memory

## Architecture

```
main.py              CLI entrypoint (Typer)
core/agent.py        LLM orchestration & context building
database/models.py   SQLModel schemas (conversations, preferences)
database/connection.py   SQLite engine & session management
memory/vector_store.py   ChromaDB persistent vector memory
config.py            Paths, defaults, environment settings
```

## Data

All data lives under `~/.config/vektor/`:
- `vektor.db` — SQLite database with conversation logs and user preferences
- `chroma_db/` — Persistent ChromaDB vector index
