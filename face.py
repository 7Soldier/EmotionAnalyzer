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


# Импорт необходимых библиотек для работы с изображениями и эмоциями
import cv2  # Импорт библиотеки OpenCV для обработки изображений и видео
from fer import FER  # Импорт библиотеки для анализа эмоций с лица
from collections import Counter  # Импорт класса Counter для подсчёта эмоций
from data import write_face_emotions  # Импорт функции записи результатов в Excel

# Определение класса FaceEmotionDetector для обнаружения лиц и распознавания эмоций
class FaceEmotionDetector:
    # Конструктор класса, принимает очередь сообщений для управления завершением работы
    def __init__(self, message_queue):
        self.face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")  # Инициализируем классификатор для распознавания лиц
        self.video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Инициализируем видеопоток с веб-камеры с использованием DirectShow
        self.emotion_analyzer = FER(mtcnn=True)  # Инициализируем анализатор эмоций с использованием MTCNN для обнаружения лиц
        self.emotion_counts = Counter()  # Инициализируем счётчик для накопления результатов эмоций
        self.message_queue = message_queue  # Сохраняем ссылку на очередь сообщений, используемую для обмена сигналами

        # Проверка успешного открытия видеопотока
        if not self.video_capture.isOpened():
            raise Exception("Невозможно открыть веб-камеру")  # Генерируем исключение, если камера не может быть открыта

    # Метод для обнаружения лиц на переданном кадре
    def detect_faces(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Преобразуем цветной кадр в оттенки серого
        # Обнаруживаем лица с помощью каскадного классификатора; scaleFactor - уменьшение изображения, minNeighbors - точность
        faces = self.face_detector.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=15)
        return faces  # Возвращаем список найденных лиц

    # Метод для распознавания эмоций для конкретного обнаруженного лица
    def detect_emotion(self, frame, face_coords):
        x, y, w, h = face_coords  # Распаковка координат лица: x, y, ширина и высота
        face_region = frame[y:y+h, x:x+w]  # Выделяем область лица из кадра
        emotion, score = self.emotion_analyzer.top_emotion(face_region)  # Определяем доминирующую эмоцию и её оценку
        self.emotion_counts[emotion] += 1  # Увеличиваем счётчик для найденной эмоции
        return emotion  # Возвращаем определённую эмоцию

    # Основной метод для запуска цикла обработки видеопотока
    def main(self):
        # В бесконечном цикле обрабатываем кадры с камеры
        while self.video_capture.isOpened():
            # Если в очереди сообщений есть команда, обрабатываем её
            if not self.message_queue.empty():
                message = self.message_queue.get()  # Получаем сообщение из очереди
                if message == 'face_exit':  # Если получен сигнал завершения работы
                    # Записываем накопленные результаты эмоций в файл Excel
                    write_face_emotions(self.emotion_counts)
                    self._cleanup()  # Вызываем метод очистки ресурсов
                    break  # Выходим из цикла

            ret, frame = self.video_capture.read()  # Захватываем кадр с камеры
            if not ret:  # Если кадр не был получен
                break  # Прерываем цикл

            faces = self.detect_faces(frame)  # Обнаруживаем лица на текущем кадре

            # Для каждого обнаруженного лица обрабатываем распознавание эмоций и визуализацию
            for face_coords in faces:
                x, y, w, h = face_coords  # Распаковка координат для рисования рамки
                # Рисуем прямоугольник вокруг найденного лица
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                emotion_label = self.detect_emotion(frame, face_coords)  # Определяем эмоцию лица
                # Отображаем текст с эмоцией над прямоугольником
                cv2.putText(frame, emotion_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.imshow("Face Emotion Detector", frame)  # Отображаем обработанный кадр

            # Если нажата клавиша 'q', завершаем работу (альтернативный способ выхода)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                write_face_emotions(self.emotion_counts)  # Сохраняем результаты в Excel
                self._cleanup()  # Очищаем ресурсы
                break  # Выходим из цикла

        self._cleanup()  # Очищаем ресурсы по окончании работы

    # Метод для очистки ресурсов (закрытие камеры и окон)
    def _cleanup(self):
        self.video_capture.release()  # Освобождаем камеру
        cv2.destroyAllWindows()  # Закрываем все окна OpenCV
