from services.audio_service import transcribe_microphone, speak as _speak


def listen(timeout: float = 5.0) -> str:
    return transcribe_microphone(timeout=timeout)


def speak(text: str) -> None:
    _speak(text)
