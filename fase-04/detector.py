import os
import cv2
from collections import defaultdict
from ultralytics import YOLO
from deepface import DeepFace
import ffmpeg

# Forçar uso de CPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
try:
    import tensorflow as tf
    tf.config.set_visible_devices([], 'GPU')
except Exception:
    pass

def fix_video_codec(input_path, output_path):
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vcodec='libx264', crf=23, preset='fast')
            .overwrite_output()
            .run(quiet=True)
        )
        os.remove(input_path)
    except ffmpeg.Error as e:
        print("Erro no ffmpeg:", e)

def detect_emotions(input_video_path, output_raw_path, output_fixed_path, progress_callback=None):
    model = YOLO("yolov8n-face.pt")
    cap = cv2.VideoCapture(input_video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    emotion_counts = defaultdict(int)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_raw_path, fourcc, fps, (width, height))

    for i in range(total):
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, verbose=False)[0]
        for box in results.boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = [int(v) for v in box]
            face_img = frame[y1:y2, x1:x2]

            if face_img.shape[0] < 50 or face_img.shape[1] < 50:
                continue

            try:
                emotion = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)[0]['dominant_emotion']
                emotion_counts[emotion] += 1
                color = (0, 255, 0)
            except:
                emotion = "Erro"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, emotion, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        out.write(frame)

        if progress_callback:
            progress_callback(min((i + 1) / total, 1.0))

    cap.release()
    out.release()
    fix_video_codec(output_raw_path, output_fixed_path)

    return total, dict(emotion_counts)
