import io
import wave

import numpy as np
import sounddevice as sd
import speech_recognition as sr

RATE = 16000
DURATION = 5
CHANNELS = 1


def listen(timeout: float = 5.0) -> str:
    recording = sd.rec(int(RATE * timeout), samplerate=RATE, channels=CHANNELS, dtype='int16')
    sd.wait()

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(recording.tobytes())
    buf.seek(0)

    r = sr.Recognizer()
    with sr.AudioFile(buf) as source:
        audio = r.record(source)

    return r.recognize_google(audio)


def speak(text: str) -> None:
    import pyttsx3
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception:
        try:
            import subprocess
            subprocess.run(["espeak", text], capture_output=True, timeout=10)
        except Exception:
            pass
