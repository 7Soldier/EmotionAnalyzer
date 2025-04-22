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

# Импортируем библиотеки для работы с данными и сохранения результатов
import pandas as pd  # Импорт библиотеки pandas для работы с табличными данными

# Функция для записи результатов распознавания эмоций лица в Excel файл
def write_face_emotions(emotion_counter):
    # Преобразуем счетчик эмоций в список кортежей и создаем DataFrame
    df = pd.DataFrame(list(emotion_counter.items()), columns=['Emotion', 'Count'])
    # Сохраняем DataFrame в Excel файл без индекса, в лист "face"
    df.to_excel('emotions_face.xlsx', index=False, sheet_name='face')

# Функция для записи результатов распознавания эмоций речи в Excel файл
def write_speech_emotions(emotion_counter):
    # Преобразуем счетчик эмоций в список кортежей и создаем DataFrame
    df = pd.DataFrame(list(emotion_counter.items()), columns=['Emotion', 'Count'])
    # Сохраняем DataFrame в Excel файл без индекса, в лист "speech"
    df.to_excel('emotions_speech.xlsx', index=False, sheet_name='speech')
