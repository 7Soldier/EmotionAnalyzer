# Copyright 2024 (c) 7Soldier <reg.fm4@gmail.com>. All Rights Reserved.
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
import cv2
from fer import FER
from collections import Counter
from data import write_face_emotions

# Определяем класс FaceEmotionDetector
class FaceEmotionDetector:
    # Инициализируем класс с очередью сообщений в качестве аргумента
    def __init__(self, message_queue):
        # Загружаем каскад Хаара для обнаружения лиц
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Открываем видеопоток с веб-камеры

        self.emotion_detector = FER(mtcnn=True)  # Инициализируем детектор эмоций
        self.emotions_counter = Counter()  # Инициализируем счетчик для подсчета эмоций
        self.message_queue = message_queue  # Сохраняем очередь сообщений

        # Если видеопоток не открыт, вызываем исключение
        if not self.video.isOpened():
            raise Exception("Cannot open webcam")

    # Метод для обнаружения лиц на кадре
    def detect_faces(self, frame):
        # Обесцвечиваем кадр
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Обнаруживаем лица на кадре
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=15)

        return faces

    # Метод для обнаружения эмоций на лицах
    def detect_emotion(self, frame, faces):
        for (x, y, w, h) in faces:
            # Обнаруживаем эмоцию на лице
            emotion = self.emotion_detector.top_emotion(frame)[0]
            # Увеличиваем счетчик для этой эмоции
            self.emotions_counter[emotion] += 1

    # Основной метод для запуска детектора
    def main(self):
        # Пока видеопоток открыт
        while self.video.isOpened():
            # Если в очереди сообщений есть сообщения
            if not self.message_queue.empty():
                message = self.message_queue.get()  # Получаем сообщение из очереди
                # Если сообщение - 'face_exit'
                if message == 'face_exit':
                    write_face_emotions(self.emotions_counter)  # Записываем эмоции в файл
                    self.video.release()  # Освобождаем видеопоток
                    cv2.destroyAllWindows()  # Закрываем все окна
                    break  # Прерываем цикл

            ret, frame = self.video.read()  # Читаем кадр из видеопотока
            faces = self.detect_faces(frame)  # Обнаруживаем лица на кадре
            self.detect_emotion(frame, faces)  # Обнаруживаем эмоции на лицах
