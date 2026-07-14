import uuid
from pathlib import Path

from config import DATA_DIR

WORKSPACE_DIR = DATA_DIR / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def generate_page(html_content: str) -> Path:
    name = f"page-{uuid.uuid4().hex[:8]}"
    filepath = WORKSPACE_DIR / f"{name}.html"
    filepath.write_text(html_content, encoding="utf-8")
    return filepath


def scaffold_project(project_name: str, files: dict[str, str]) -> Path:
    project_dir = WORKSPACE_DIR / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        full = project_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    return project_dir
