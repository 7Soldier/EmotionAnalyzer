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

# Импорт необходимых библиотек для управления потоками и работы с клавиатурой
import keyboard  # Библиотека для отслеживания нажатия клавиш
import threading  # Библиотека для работы с потоками
import queue  # Модуль для создания очередей
from speech import SpeechEmotionDetector  # Импорт класса детектора эмоций речи
from face import FaceEmotionDetector  # Импорт класса детектора эмоций лица

# Функция для обработки сигнала выхода из программы по нажатию клавиши 'q'
def exit_handler(message_queue):
    keyboard.wait('q')  # Ждём, пока пользователь не нажмёт клавишу 'q'
    message_queue.put('face_exit')  # Отправляем сигнал выхода для детектора лица
    message_queue.put('recording_exit')  # Отправляем сигнал выхода для потока записи аудио
    message_queue.put('speech_exit')  # Отправляем сигнал выхода для детектора речи (запись звука)
    message_queue.put('speech_exit')  # Отправляем сигнал выхода для детектора речи (анализ эмоций)

# Основная функция, создающая и запускающая потоки для детекторов и обработки выхода
def main():
    # Инициализируем общую очередь сообщений для всех потоков
    message_queue = queue.Queue()  # Создание очереди сообщений
    # Создаём экземпляры детекторов, передавая в них очередь сообщений
    speech_detector = SpeechEmotionDetector(message_queue)
    face_detector = FaceEmotionDetector(message_queue)

    # Создаём поток для детектора речи; target передаём как метод main объекта
    speech_thread = threading.Thread(target=speech_detector.main)
    # Создаём поток для детектора лица; target передаём как метод main
    face_thread = threading.Thread(target=face_detector.main)
    # Создаём поток для обработки события выхода по клавише 'q'
    interrupt_thread = threading.Thread(target=exit_handler, args=(message_queue,))

    # Запускаем созданные потоки
    speech_thread.start()  # Запуск потока детектора речи
    face_thread.start()  # Запуск потока детектора лица
    interrupt_thread.start()  # Запуск потока для обработки сигнала выхода

    # Ждем, пока все потоки завершат свою работу
    speech_thread.join()  # Ожидание завершения потока детектора речи
    face_thread.join()  # Ожидание завершения потока детектора лица
    interrupt_thread.join()  # Ожидание завершения потока обработки выхода

# Если данный файл запущен как основной, запускаем main функцию
if __name__ == "__main__":
    main()  # Запуск основной функции