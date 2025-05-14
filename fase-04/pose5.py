import argparse
import cv2
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO
import mediapipe as mp

# =======================
# Configurações
# =======================
mp_pose = mp.solutions.pose
pose_estimator = mp_pose.Pose(
    static_image_mode=False, model_complexity=1, enable_segmentation=False
)
previous_keypoints = {}


# =======================
# Utilitários de vídeo
# =======================
def setup_video_io(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video = cv2.VideoWriter(f"output-{video_path}", fourcc, fps, (width, height))
    return cap, output_video, fps, width, height, total_frames


# =======================
# Pose com MediaPipe
# =======================
def extract_mediapipe_keypoints(person_crop):
    rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
    result = pose_estimator.process(rgb)
    if result.pose_landmarks:
        keypoints = []
        for lm in result.pose_landmarks.landmark:
            x = int(lm.x * person_crop.shape[1])
            y = int(lm.y * person_crop.shape[0])
            keypoints.append((x, y))
        return keypoints
    return None


# =======================
# Lógica de caminhada
# =======================
def is_walking(track_id, current_kps, threshold=5):
    global previous_keypoints
    walking = False
    ankle_indices = [27, 28]  # tornozelos no MediaPipe

    if track_id in previous_keypoints:
        prev_kps = previous_keypoints[track_id]
        displacements = []
        for i in ankle_indices:
            if i < len(current_kps) and i < len(prev_kps):
                dx = current_kps[i][0] - prev_kps[i][0]
                dy = current_kps[i][1] - prev_kps[i][1]
                displacement = np.sqrt(dx**2 + dy**2)
                displacements.append(displacement)

        if displacements:
            avg_disp = np.mean(displacements)
            if avg_disp > threshold:
                walking = True

    previous_keypoints[track_id] = current_kps
    return walking


# =======================
# Processamento principal
# =======================
def process_video(video_path, model_path="yolov8x.pt"):
    model = YOLO(model_path)
    cap, output_video, fps, width, height, total_frames = setup_video_io(video_path)
    progress_bar = tqdm(total=total_frames, desc="Processando", unit="frame")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        progress_bar.update(1)
        annotated_image = frame.copy()

        # YOLO + Tracking
        results = model.track(source=frame, persist=True, classes=0, verbose=False)
        r = results[0]

        if r.boxes is not None and r.boxes.id is not None:
            for box, track_id in zip(r.boxes.xyxy, r.boxes.id):
                x1, y1, x2, y2 = map(int, box.tolist())
                pid = int(track_id.item())
                color = (0, 255, 0)

                # Recorte da pessoa
                person_crop = frame[y1:y2, x1:x2]
                keypoints = extract_mediapipe_keypoints(person_crop)

                status = []
                if keypoints:
                    # Verificação de caminhada
                    absolute_kps = [(x1 + x, y1 + y) for x, y in keypoints]
                    if is_walking(pid, absolute_kps):
                        status.append("andando")

                    # Desenho dos keypoints (opcional)
                    for px, py in absolute_kps:
                        cv2.circle(annotated_image, (px, py), 3, color, -1)

                # Caixa + status
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
                if status:
                    cv2.putText(
                        annotated_image,
                        ", ".join(status),
                        (x1 + 5, y2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2,
                    )

        # Grava frame
        output_video.write(annotated_image)

        # Exibir (opcional)
        cv2.imshow("Tracking com Pose", annotated_image)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Finalização
    progress_bar.close()
    cap.release()
    output_video.release()
    cv2.destroyAllWindows()
    print("Processamento finalizado com sucesso!")


# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Detector de caminhada com YOLO + MediaPipe"
    )
    parser.add_argument("video_path", type=str, help="Caminho do vídeo")
    parser.add_argument(
        "--model_path",
        type=str,
        default="yolov8x.pt",
        help="Caminho do modelo YOLO (sem pose)",
    )
    args = parser.parse_args()

    process_video(args.video_path, args.model_path)
