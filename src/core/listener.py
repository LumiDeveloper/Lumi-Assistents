import os
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
from PyQt6.QtCore import QThread, pyqtSignal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "model")

class SpeechWorker(QThread):
    # Этот сигнал отправит текст в наше GUI окно
    text_recognized = pyqtSignal(str)

    def __init__(self, device_id):
        super().__init__()
        if not os.path.exists(MODEL_PATH):
            raise Exception(f"Папка модели не найдена по пути: {MODEL_PATH}")
        self.model = Model(MODEL_PATH)
        self.samplerate = 16000
        self.device_id = device_id
        self.q = queue.Queue()

    def callback(self, indata, frames, time, status):
        """Функция захвата кусочков звука"""
        self.q.put(bytes(indata))

    def run(self):
        # Открываем поток именно с твоим USB-ID
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, 
                               device=self.device_id, dtype='int16', 
                               channels=1, callback=self.callback):
            
            rec = KaldiRecognizer(self.model, self.samplerate)
            print(">>> Люми начала слушать...")
            
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '')
                    if text:
                        self.text_recognized.emit(text)