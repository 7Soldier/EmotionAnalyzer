# Copyright 2025 (c) 7Soldier <reg.fm4@gmail.com>. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Импортируем необходимые библиотеки
import os
import queue
import sounddevice as sd
import threading
import scipy.io.wavfile as wav
import torch
from aniemore.recognizers.multimodal import MultiModalRecognizer
from aniemore.utils.speech2text import SmallSpeech2Text
from aniemore.models import HuggingFaceModel
from collections import Counter
from data import write_speech_emotions

# Определение класса для обнаружения эмоций в речи
class SpeechEmotionDetector:
    # Инициализируем класс с очередью сообщений в качестве аргумента
    def __init__(self, message_queue):
        # Инициализация модели для распознавания эмоций
        self.model = HuggingFaceModel.MultiModal.WavLMBertFusion
        # Определение устройства для работы с моделью
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # Инициализация распознавателя эмоций
        self.mr = MultiModalRecognizer(model=self.model, s2t_model=SmallSpeech2Text(), device=self.device)

        self.emotions_counter = Counter()  # Инициализация счетчика эмоций
        self.wav_queue = queue.Queue()  # Инициализация очереди для wav-файлов
        self.message_queue = message_queue  # Сохранение очереди сообщений

        self.recording_path = './recording/'  # Путь для сохранения записей
        self.recording_duration = 10  # Длительность записи
        self.fs = 44100  # Частота дискретизации
        self.channels = 1  # Количество каналов

    # Метод для записи аудио
    def record_audio(self):
        counter = 0  # Счетчик для именования файлов
        while True:  # Бесконечный цикл
            if not self.message_queue.empty():  # Если в очереди сообщений есть сообщения
                message = self.message_queue.get()  # Получение сообщения из очереди
                if message == 'recording_exit':  # Если сообщение о завершении записи
                    break  # Прерывание цикла

            # Запись аудио
            recording = sd.rec(int(self.recording_duration * self.fs), samplerate=self.fs, channels=self.channels)
            sd.wait()  # Ожидание окончания записи
            filename = os.path.join(self.recording_path, f'output_{counter}.wav')  # Создание имени файла
            wav.write(filename, self.fs, recording)  # Запись аудио в файл
            self.wav_queue.put(filename)  # Добавление имени файла в очередь
            counter += 1  # Увеличение счетчика

    # Метод для анализа эмоций
    def analyze_emotion(self):
        while True:  # Бесконечный цикл
            if not self.message_queue.empty():  # Если в очереди сообщений есть сообщения
                message = self.message_queue.get()  # Получение сообщения из очереди
                if message == 'speech_exit':  # Если сообщение о завершении анализа
                    write_speech_emotions(self.emotions_counter)  # Запись эмоций в файл
                    files = [f for f in os.listdir(self.recording_path)]  # Получение списка файлов в директории
                    for file in files:  # Для каждого файла
                        os.remove(os.path.join(self.recording_path, file))  # Удаление файла
                    break  # Прерывание цикла

            filename = self.wav_queue.get()  # Получение имени файла из очереди
            emotion = self.mr.recognize(filename, return_single_label=True)  # Распознавание эмоции в аудио
            self.emotions_counter[emotion] += 1  # Увеличение счетчика для полученной эмоции
            os.remove(filename)  # Удаление файла после анализа

    # Основной метод для запуска детектора
    def main(self):
        record_thread = threading.Thread(target=self.record_audio)  # Создание потока для записи аудио
        analyze_thread = threading.Thread(target=self.analyze_emotion)  # Создание потока для анализа эмоций
        record_thread.start()  # Запуск потока для записи аудио
        analyze_thread.start()  # Запуск потока для анализа эмоций
