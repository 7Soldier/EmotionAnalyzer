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

# Импорт необходимых библиотек для записи и обработки аудио, а также для распознавания эмоций
import os  # Модуль для работы с операционной системой
import queue  # Модуль для реализации очередей
import sounddevice as sd  # Библиотека для записи аудио
import threading  # Библиотека для работы с потоками
import scipy.io.wavfile as wav  # Модуль для записи WAV файлов
import torch  # Библиотека для работы с тензорами и устройствами (CPU/GPU)
from aniemore.recognizers.multimodal import MultiModalRecognizer  # Импорт мультимодального распознавателя
from aniemore.utils.speech2text import SmallSpeech2Text  # Импорт утилиты для преобразования речи в текст
from aniemore.models import HuggingFaceModel  # Импорт моделей из HuggingFace
from collections import Counter  # Импорт класса для подсчёта эмоций
from data import write_speech_emotions  # Импорт функции записи результатов в Excel

# Определение класса SpeechEmotionDetector для распознавания эмоций речи
class SpeechEmotionDetector:
    # Конструктор, принимающий очередь сообщений для управления завершением работы
    def __init__(self, message_queue):
        # Определяем модель для мультимодального распознавания речи с эмоциями
        self.multi_modal_model = HuggingFaceModel.MultiModal.WavLMBertFusion
        # Определяем устройство (GPU или CPU) для работы модели
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # Инициализируем мультимодальный распознаватель, передавая модель и speech-to-text преобразователь
        self.multi_modal_recognizer = MultiModalRecognizer(model=self.multi_modal_model,
                                                           s2t_model=SmallSpeech2Text(),
                                                           device=self.device)
        self.emotion_counts = Counter()  # Инициализируем счётчик для накопления распознанных эмоций речи
        self.audio_file_queue = queue.Queue()  # Инициализируем очередь для хранения имен файлов с записями аудио
        self.message_queue = message_queue  # Сохраняем ссылку на очередь сообщений

        self.recording_path = './recording/'  # Задаём путь для сохранения аудиозаписей
        self.recording_duration_sec = 10  # Длительность одной записи в секундах
        self.sampling_rate = 44100  # Частота дискретизации аудио
        self.num_channels = 1  # Количество звуковых каналов

    # Метод для записи аудио с микрофона и сохранения записей в файлы
    def record_audio(self):
        file_counter = 0  # Счётчик для формирования уникальных имён файлов
        # Бесконечный цикл записи аудио
        while True:
            # Проверяем, есть ли в очереди сообщение о завершении записи
            if not self.message_queue.empty():
                exit_message = self.message_queue.get()  # Извлекаем сообщение
                if exit_message == 'recording_exit':  # Если получен сигнал завершения
                    break  # Прерываем цикл записи

            # Записываем аудио длительностью recording_duration_sec секунд
            audio_recording = sd.rec(int(self.recording_duration_sec * self.sampling_rate),
                                     samplerate=self.sampling_rate,
                                     channels=self.num_channels)
            sd.wait()  # Ожидаем завершения записи аудио
            # Формируем имя файла для записи с уникальным счётчиком
            audio_filename = os.path.join(self.recording_path, f'output_{file_counter}.wav')
            wav.write(audio_filename, self.sampling_rate, audio_recording)  # Сохраняем аудиозапись в WAV файл
            self.audio_file_queue.put(audio_filename)  # Добавляем имя файла в очередь обработки
            file_counter += 1  # Увеличиваем счётчик для следующей записи

    # Метод для анализа аудиозаписей на выявление эмоций
    def analyze_emotion(self):
        # Бесконечный цикл обработки аудио файлов
        while True:
            # Проверяем, есть ли в очереди сообщения о завершении анализа
            if not self.message_queue.empty():
                exit_message = self.message_queue.get()  # Извлекаем сообщение
                if exit_message == 'speech_exit':  # Если сигнал завершения получен
                    # Записываем накопленные результаты эмоций речи в Excel файл
                    write_speech_emotions(self.emotion_counts)
                    # Получаем список всех файлов в директории с записями
                    recorded_files = [f for f in os.listdir(self.recording_path)]
                    for file in recorded_files:  # Удаляем каждый файл записи
                        os.remove(os.path.join(self.recording_path, file))
                    break  # Прерываем цикл анализа

            # Получаем имя файла из очереди аудиофайлов (блокирующий вызов)
            audio_filename = self.audio_file_queue.get()
            # Распознаем эмоцию для аудиофайла; возвращается единственная метка эмоции
            recognized_emotion = self.multi_modal_recognizer.recognize(audio_filename, return_single_label=True)
            self.emotion_counts[recognized_emotion] += 1  # Увеличиваем счётчик для полученной эмоции
            os.remove(audio_filename)  # Удаляем обработанный файл аудио для экономии места

    # Основной метод для запуска потоков записи и анализа аудио
    def main(self):
        # Создаём поток для записи аудио с микрофона
        recording_thread = threading.Thread(target=self.record_audio)
        # Создаём поток для анализа записанных аудио файлов
        analysis_thread = threading.Thread(target=self.analyze_emotion)
        recording_thread.start()  # Запускаем поток записи аудио
        analysis_thread.start()  # Запускаем поток анализа аудио
        # Потоки продолжают работу независимо, основной поток завершится после join-ов (если потребуется)
        recording_thread.join()  # Ожидаем завершения потока записи
        analysis_thread.join()  # Ожидаем завершения потока анализа


