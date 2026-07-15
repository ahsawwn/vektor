import io
import os
import subprocess
import tempfile
import wave

import speech_recognition as sr


def listen(timeout: float = 5.0) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name

    try:
        subprocess.run(
            ["arecord", "-r", "16000", "-f", "S16_LE", "-c", "1", "-d", str(int(timeout)), tmp],
            capture_output=True,
            timeout=timeout + 5,
        )

        r = sr.Recognizer()
        with sr.AudioFile(tmp) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def speak(text: str) -> None:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception:
        try:
            subprocess.run(["espeak", text], capture_output=True, timeout=10)
        except Exception:
            pass
