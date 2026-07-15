import asyncio
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from config import OLLAMA_HOST, OLLAMA_MODEL
from core.agent import VektorAgent
from database.connection import engine
from database.models import UserPreference

from . import commands, database as db, memory_vector, voice_engine

_HERE = Path(__file__).resolve().parent
_FRONTEND_DIST = _HERE.parent / "frontend" / "dist"

_active_connections: set[WebSocket] = set()
_agent = VektorAgent()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_LEARN_RE = re.compile(
    r"(?:remember|learn)\s+that\s+(.+?)\s+(?:is|uses?|has|prefers?|runs?on)\s+(.+)",
    re.IGNORECASE,
)
_REMEMBER_RE = re.compile(
    r"(?:remember|learn)\s+['\"](.+?)['\"]\s+(?:as|is|=|->)\s+['\"](.+?)['\"]",
    re.IGNORECASE,
)


async def _broadcast(data: dict) -> None:
    msg = json.dumps(data)
    for ws in _active_connections.copy():
        try:
            await ws.send_text(msg)
        except Exception:
            _active_connections.discard(ws)


async def _handle_chat(user_text: str, ws: WebSocket) -> None:
    learn_m = _LEARN_RE.match(user_text) or _REMEMBER_RE.match(user_text)
    if learn_m:
        key = learn_m.group(1).strip().lower().replace(" ", "_")
        value = learn_m.group(2).strip()
        db.set_preference(key, value)
        await ws.send_json({"type": "memory", "key": key, "value": value})
        await ws.send_json({"type": "message", "role": "assistant", "content": f"Stored: `{key}` → `{value}`"})
        return

    db.save_message("user", user_text)
    history = db.get_recent_messages(5)
    memories = memory_vector.query_memories(user_text)
    prefs = db.get_preferences()

    pref_text = "\n".join(f"  {k}: {v}" for k, v in prefs.items()) if prefs else ""
    mem_text = "\n".join(f"- {m}" for m in memories) if memories else ""

    system_parts = [
        "You are Vektor, a persistent local AI assistant.",
        "Technical, concise, precise. Short answers, dense information.",
    ]
    if pref_text:
        system_parts.append(f"User preferences:\n{pref_text}")
    if mem_text:
        system_parts.append(f"Related context:\n{mem_text}")

    messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_text})

    loop = asyncio.get_event_loop()

    def _do_chat():
        import ollama
        client = ollama.Client(host=OLLAMA_HOST)
        resp = client.chat(model=OLLAMA_MODEL, messages=messages)
        return resp["message"]["content"]

    reply = await loop.run_in_executor(None, _do_chat)

    aid = db.save_message("assistant", reply)
    memory_vector.add_memory(aid, f"User: {user_text}")
    memory_vector.add_memory(aid + 1, f"Vektor: {reply}")

    await ws.send_json({"type": "message", "role": "assistant", "content": reply})

    scaffold_match = re.search(
        r"(?:build|create|generate|scaffold)\s+(?:a\s+)?.*?(?:page|site|landing|ui|html)",
        user_text,
        re.IGNORECASE,
    )
    if scaffold_match:
        html_match = re.search(r"(<!DOCTYPE html>.*?</html>)", reply, re.DOTALL)
        if html_match:
            from services.web_scaffolder import generate_page
            path = generate_page(html_match.group(1))
            await ws.send_json({"type": "preview", "path": str(path)})

    safe, reason = commands.check_safe(user_text)
    if not safe and any(cmd in user_text.lower() for cmd in ("list", "show", "create", "make", "run", "delete", "remove", "copy", "move")):
        pass
    cmd_keywords = ["list", "ls", "cat", "echo", "mkdir", "touch", "pwd", "whoami", "date", "uname", "df", "du", "head", "tail"]
    if any(kw in user_text.lower().split() for kw in cmd_keywords):
        import shlex
        def _do_exec():
            return commands.run(user_text)
        output = await loop.run_in_executor(None, _do_exec)
        await ws.send_json({"type": "command", "output": output})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _active_connections.add(ws)
    await ws.send_json({"type": "status", "state": "idle", "model": OLLAMA_MODEL})
    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                await ws.send_json({"type": "status", "state": "thinking"})
                await _handle_chat(data["text"], ws)
                await ws.send_json({"type": "status", "state": "idle"})

            elif msg_type == "voice":
                await ws.send_json({"type": "status", "state": "listening"})
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(None, voice_engine.listen)
                if text:
                    await ws.send_json({"type": "voice_text", "text": text})
                    await ws.send_json({"type": "status", "state": "thinking"})
                    await _handle_chat(text, ws)
                await ws.send_json({"type": "status", "state": "idle"})

            elif msg_type == "execute":
                await ws.send_json({"type": "status", "state": "executing"})
                loop = asyncio.get_event_loop()
                output = await loop.run_in_executor(None, commands.run, data["command"])
                await ws.send_json({"type": "command", "output": output})
                await ws.send_json({"type": "status", "state": "idle"})

            elif msg_type == "remember":
                db.set_preference(data["key"], data["value"])
                await ws.send_json({"type": "memory", "key": data["key"], "value": data["value"]})

            elif msg_type == "speak":
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, voice_engine.speak, data["text"])

            elif msg_type == "history":
                msgs = db.get_recent_messages(50)
                await ws.send_json({"type": "history", "messages": msgs})

    except WebSocketDisconnect:
        _active_connections.discard(ws)


@app.get("/api/status")
async def api_status():
    return {
        "model": OLLAMA_MODEL,
        "messages": len(db.get_recent_messages(1000)),
        "preferences": db.get_preferences(),
        "vector_count": memory_vector.count(),
    }


@app.get("/api/history")
async def api_history(limit: int = 50):
    return db.get_recent_messages(limit)


_SPA_HTML = _FRONTEND_DIST / "index.html"


@app.get("/{path:path}")
async def spa(path: str):
    file = _FRONTEND_DIST / path
    if file.exists() and file.is_file():
        return FileResponse(str(file))
    if _SPA_HTML.exists():
        return FileResponse(str(_SPA_HTML))
    return {"error": "frontend not built"}, 404


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
