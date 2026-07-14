import os
import shlex
import subprocess
from pathlib import Path

ALLOWED_COMMANDS: set[str] = {
    "ls", "cat", "echo", "mkdir", "touch", "cp", "mv", "rm",
    "chmod", "pwd", "whoami", "date", "uname", "df", "du",
    "head", "tail", "wc", "sort", "grep", "find",
}

FORBIDDEN_PATTERNS: list[str] = [
    "rm -rf /",
    "rm -rf ~",
    "mkfs",
    "dd",
    "> /dev/",
    "sudo",
    "su ",
    "chown",
    "passwd",
    "reboot",
    "shutdown",
    "init ",
    "kill ",
    "pkill ",
]


def is_safe(command: str) -> tuple[bool, str]:
    cmd = command.strip()
    if not cmd:
        return False, "empty command"

    for pattern in FORBIDDEN_PATTERNS:
        if pattern in cmd:
            return False, f"forbidden pattern: {pattern}"

    parts = shlex.split(cmd)
    if not parts:
        return False, "could not parse command"

    base = os.path.basename(parts[0])
    if base not in ALLOWED_COMMANDS:
        return False, f"command not allowed: {base}"

    return True, ""


def execute(command: str) -> str:
    safe, reason = is_safe(command)
    if not safe:
        return f"[DENIED] {reason}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"[stderr]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR] command timed out (30s)"
    except Exception as e:
        return f"[ERROR] {e}"
