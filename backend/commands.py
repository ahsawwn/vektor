from services.executor_service import execute as _execute, is_safe


def check_safe(command: str) -> tuple[bool, str]:
    return is_safe(command)


def run(command: str) -> str:
    return _execute(command)
