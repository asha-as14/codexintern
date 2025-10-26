import speech_recognition as sr
import pyttsx3
import time

class SpeechEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # adjust for ambient noise once
        with sr.Microphone() as source:
            print("Calibrating microphone for ambient noise... Please be quiet.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        # TTS
        self.tts_engine = pyttsx3.init()
        self.set_tts_properties()

    def set_tts_properties(self):
        # adjust rate and volume if desired
        rate = self.tts_engine.getProperty('rate')
        self.tts_engine.setProperty('rate', rate - 15)
        vol = self.tts_engine.getProperty('volume')
        self.tts_engine.setProperty('volume', vol)

    def speak(self, text):
        print("Assistant:", text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self, timeout=5, phrase_time_limit=6, wake_word=None):
        """
        Listen and return recognized text or None.
        If wake_word provided, this method will still return the recognized utterance (caller should detect wake word).
        """
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return None
        try:
            text = self.recognizer.recognize_google(audio)
            print("Heard:", text)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print("Speech recognition error:", e)
            return None
