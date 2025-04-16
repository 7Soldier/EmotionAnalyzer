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
import keyboard
import threading
import queue
from speech import SpeechEmotionDetector
from face import FaceEmotionDetector

# Функция для обработки выхода из программы
def exit_handler():
    keyboard.wait('q')  # Ожидание нажатия клавиши 'q'
    message_queue.put('face_exit')  # Добавление сообщения в очередь
    message_queue.put('recording_exit')  # Добавление сообщения в очередь
    message_queue.put('speech_exit')  # Добавление сообщения в очередь

# Главная функция
def main():
    # Создание потока для обнаружения эмоций в голосе
    voice_thread = threading.Thread(target=SpeechEmotionDetector(message_queue).main)
    # Создание потока для обнаружения эмоций на лице
    face_thread = threading.Thread(target=FaceEmotionDetector(message_queue).main)
    # Создание потока для обработки выхода из программы
    interrupt_thread = threading.Thread(target=exit_handler)

    # Запуск потоков
    voice_thread.start()
    face_thread.start()
    interrupt_thread.start()

    # Ожидание завершения потоков
    voice_thread.join()
    face_thread.join()
    interrupt_thread.join()

# Если этот файл является главным, то запускается главная функция
if __name__ == "__main__":
    message_queue = queue.Queue()  # Создание очереди сообщений
    main()  # Запуск главной функции
