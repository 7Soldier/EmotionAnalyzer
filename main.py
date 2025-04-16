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
def exit_handler(face_exit_event, recording_exit_event, speech_exit_event):
    keyboard.wait('q')  # Ожидание нажатия клавиши 'q'
    face_exit_event.set()  # Установка события для выхода face
    recording_exit_event.set()  # Установка события для выхода recording
    speech_exit_event.set()  # Установка события для выхода speech

# Главная функция
def main():
    # Создание событий для сигнализации
    face_exit_event = multiprocessing.Event()
    recording_exit_event = multiprocessing.Event()
    speech_exit_event = multiprocessing.Event()

    # Создание процессов для обнаружения эмоций
    voice_process = multiprocessing.Process(
        target=SpeechEmotionDetector(recording_exit_event, speech_exit_event).main
    )
    face_process = multiprocessing.Process(
        target=FaceEmotionDetector(face_exit_event).main
    )
    interrupt_process = multiprocessing.Process(
        target=exit_handler, args=(face_exit_event, recording_exit_event, speech_exit_event)
    )

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
    main()  # Запуск главной функции
