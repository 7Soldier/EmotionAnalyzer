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
import pandas as pd

# Функция для записи эмоций лица в файл Excel
def write_face_emotions(emotions_counter):
    # Создаем DataFrame из словаря счетчика эмоций
    df = pd.DataFrame(list(emotions_counter.items()), columns=['Emotion', 'Count'])
    # Сохраняем DataFrame в файл Excel
    df.to_excel('emotions_face.xlsx', index=False, sheet_name='face')

# Функция для записи эмоций речи в файл Excel
def write_speech_emotions(emotions_counter):
    # Создаем DataFrame из словаря счетчика эмоций
    df = pd.DataFrame(list(emotions_counter.items()), columns=['Emotion', 'Count'])
    # Сохраняем DataFrame в файл Excel
    df.to_excel('emotions_speech.xlsx', index=False, sheet_name='speech')