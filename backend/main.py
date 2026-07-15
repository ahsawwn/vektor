import asyncio
import json
import os
import re
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, WORKSPACE_DIR
from core.agent import VektorAgent

from . import commands, database as db, memory_vector, voice_engine

_HERE = Path(__file__).resolve().parent
_FRONTEND_DIST = _HERE.parent / "frontend" / "dist"
_SPA_HTML = _FRONTEND_DIST / "index.html"
_UPLOAD_DIR = WORKSPACE_DIR / "uploads"
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_active_connections: set[WebSocket] = set()
_agent = VektorAgent()
_has_greeted = False


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_LEARN_RE = re.compile(
    r"(?:remember|learn)\s+that\s+(.+?)\s+(?:is|uses?|has|prefers?|runs?on)\s+(.+)",
    re.IGNORECASE,
)
_REMEMBER_RE = re.compile(
    r"(?:remember|learn)\s+['\"](.+?)['\"]\s+(?:as|is|=|->)\s+['\"](.+?)['\"]",
    re.IGNORECASE,
)


async def _llm_chat(messages: list[dict]) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"model": OPENROUTER_MODEL, "messages": messages},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


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

    system_parts = ["You are Vektor, a persistent local AI assistant.", "Technical, concise, precise."]
    if prefs:
        system_parts.append("User preferences:\n" + "\n".join(f"  {k}: {v}" for k, v in prefs.items()))
    if memories:
        system_parts.append("Related context:\n" + "\n".join(f"- {m}" for m in memories))

    messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_text})

    reply = await _llm_chat(messages)
    aid = db.save_message("assistant", reply)
    memory_vector.add_memory(aid, f"User: {user_text}")
    memory_vector.add_memory(aid + 1, f"Vektor: {reply}")
    await ws.send_json({"type": "message", "role": "assistant", "content": reply})

    cmd_keywords = ["list", "ls", "cat", "echo", "mkdir", "touch", "pwd", "whoami", "date", "uname", "df", "du", "head", "tail"]
    if any(kw in user_text.lower().split() for kw in cmd_keywords):
        def _do_exec():
            return commands.run(user_text)
        output = await asyncio.get_event_loop().run_in_executor(None, _do_exec)
        await ws.send_json({"type": "command", "output": output})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global _has_greeted
    await ws.accept()
    _active_connections.add(ws)
    await ws.send_json({"type": "status", "state": "idle", "model": OPENROUTER_MODEL})

    msg_count = db.count_messages()
    if not _has_greeted:
        _has_greeted = True
        greeting = "Vektor online. System ready."
        await ws.send_json({"type": "message", "role": "assistant", "content": greeting})
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, voice_engine.speak, greeting)
        except Exception as e:
            print(f"TTS error: {e}")

    if msg_count > 0:
        history = db.get_recent_messages(20)
        if history:
            await ws.send_json({"type": "history", "messages": history})
            await ws.send_json({"type": "message", "role": "assistant", "content": f"Session resumed. {msg_count} messages in memory."})

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
                try:
                    text = await loop.run_in_executor(None, voice_engine.listen)
                    if text:
                        await ws.send_json({"type": "voice_text", "text": text})
                        await ws.send_json({"type": "status", "state": "thinking"})
                        await _handle_chat(text, ws)
                except Exception as e:
                    await ws.send_json({"type": "message", "role": "assistant", "content": f"[voice error] {e}"})
                await ws.send_json({"type": "status", "state": "idle"})

            elif msg_type == "speak":
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, voice_engine.speak, data["text"])

            elif msg_type == "history":
                msgs = db.get_recent_messages(50)
                await ws.send_json({"type": "history", "messages": msgs})

    except WebSocketDisconnect:
        _active_connections.discard(ws)


# ── File CRUD ──────────────────────────────────────────────────────

@app.get("/api/files")
async def list_files(path: str = "."):
    base = WORKSPACE_DIR
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return JSONResponse({"error": "access denied"}, status_code=403)
    if not target.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    entries = []
    for f in sorted(target.iterdir()):
        entries.append({
            "name": f.name,
            "is_dir": f.is_dir(),
            "size": f.stat().st_size if f.is_file() else 0,
            "modified": f.stat().st_mtime,
        })
    return {"path": str(path), "entries": entries}


@app.post("/api/files/read")
async def read_file(data: dict):
    path = data.get("path", "")
    base = WORKSPACE_DIR
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return JSONResponse({"error": "access denied"}, status_code=403)
    if not target.is_file():
        return JSONResponse({"error": "not a file"}, status_code=400)
    return {"content": target.read_text(encoding="utf-8")}


@app.post("/api/files/write")
async def write_file(data: dict):
    path = data.get("path", "")
    content = data.get("content", "")
    base = WORKSPACE_DIR
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return JSONResponse({"error": "access denied"}, status_code=403)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"status": "ok", "path": str(path)}


@app.post("/api/files/mkdir")
async def make_dir(data: dict):
    path = data.get("path", "")
    base = WORKSPACE_DIR
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return JSONResponse({"error": "access denied"}, status_code=403)
    target.mkdir(parents=True, exist_ok=True)
    return {"status": "ok"}


@app.post("/api/files/delete")
async def delete_file(data: dict):
    path = data.get("path", "")
    base = WORKSPACE_DIR
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return JSONResponse({"error": "access denied"}, status_code=403)
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return {"status": "ok"}


# ── Image Upload ───────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_image(file: UploadFile):
    ext = Path(file.filename or "image.png").suffix
    name = f"{uuid.uuid4().hex}{ext}"
    dest = _UPLOAD_DIR / name
    content = await file.read()
    dest.write_bytes(content)
    return {"url": f"/uploads/{name}"}


@app.get("/uploads/{name}")
async def serve_upload(name: str):
    file = _UPLOAD_DIR / name
    if file.exists():
        return FileResponse(str(file))
    return JSONResponse({"error": "not found"}, status_code=404)


# ── Status & SPA ───────────────────────────────────────────────────

@app.get("/api/status")
async def api_status():
    return {
        "model": OPENROUTER_MODEL,
        "messages": db.count_messages(),
        "preferences": db.get_preferences(),
        "vector_count": memory_vector.count(),
    }


@app.get("/{path:path}")
async def spa(path: str):
    file = _FRONTEND_DIST / path
    if file.exists() and file.is_file():
        return FileResponse(str(file))
    if _SPA_HTML.exists():
        return FileResponse(str(_SPA_HTML))
    return JSONResponse({"error": "frontend not built"}, status_code=404)


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
