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

import keyboard
import multiprocessing
from speech import SpeechEmotionDetector
from face import FaceEmotionDetector

# Функция для обработки выхода из программы
def exit_handler(message_queue):
    keyboard.wait('q')  # Ожидание нажатия клавиши 'q'
    message_queue.put('face_exit')  # Добавление сообщения в очередь
    message_queue.put('recording_exit')  # Добавление сообщения в очередь
    message_queue.put('speech_exit')  # Добавление сообщения в очередь

# Главная функция
def main():
    # Создание процессов для обнаружения эмоций
    voice_process = multiprocessing.Process(target=SpeechEmotionDetector(message_queue).main)
    face_process = multiprocessing.Process(target=FaceEmotionDetector(message_queue).main)
    interrupt_process = multiprocessing.Process(target=exit_handler, args=(message_queue,))

    # Запуск процессов
    voice_process.start()
    face_process.start()
    interrupt_process.start()

    # Ожидание завершения процессов
    voice_process.join()
    face_process.join()
    interrupt_process.join()

# Если этот файл является главным, то запускается главная функция
if __name__ == "__main__":
    message_queue = multiprocessing.Queue()  # Создание очереди сообщений
    main()  # Запуск главной функции
