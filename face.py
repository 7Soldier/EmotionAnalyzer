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
import cv2
from fer import FER
from collections import Counter
from data import write_face_emotions

# Определяем класс FaceEmotionDetector
class FaceEmotionDetector:
    def __init__(self, message_queue):
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.emotion_detector = FER(mtcnn=True)
        self.emotions_counter = Counter()
        self.message_queue = message_queue

        if not self.video.isOpened():
            raise Exception("Cannot open webcam")

    def detect_faces(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=15)
        return faces

    def detect_emotion(self, frame, face):
        x, y, w, h = face
        face_region = frame[y:y+h, x:x+w]
        emotion, score = self.emotion_detector.top_emotion(face_region)
        self.emotions_counter[emotion] += 1
        return emotion

    def main(self):
        while self.video.isOpened():
            if not self.message_queue.empty():
                message = self.message_queue.get()
                if message == 'face_exit':
                    write_face_emotions(self.emotions_counter)
                    self.video.release()
                    cv2.destroyAllWindows()
                    break

            ret, frame = self.video.read()
            if not ret:
                break

            faces = self.detect_faces(frame)

            for face in faces:
                x, y, w, h = face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                emotion = self.detect_emotion(frame, face)
                cv2.putText(frame, emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.imshow("Face Emotion Detector", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                write_face_emotions(self.emotions_counter)
                self.video.release()
                cv2.destroyAllWindows()
                break

        self.video.release()
        cv2.destroyAllWindows()
