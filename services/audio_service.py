from queue import Queue

import pyttsx3
import speech_recognition as sr

_tts_queue: Queue = Queue()


def transcribe_microphone(timeout: float = 5.0, phrase_limit: float = 10.0) -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.3)
        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    return r.recognize_google(audio)


def speak(text: str, engine: pyttsx3.Engine | None = None) -> None:
    close = engine is None
    if engine is None:
        engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    if close:
        engine.stop()
