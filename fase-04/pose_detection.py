import argparse
import cv2
from tqdm import tqdm
from ultralytics import YOLO


# =======================
# Funções utilitárias
# =======================
def setup_video_io(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video = cv2.VideoWriter(
        video_path.replace(".mp4", "_output.mp4"), fourcc, fps, (width, height)
    )
    return cap, output_video, fps, width, height, total_frames


def get_color(idx):
    colors = [
        (0, 255, 0),
        (255, 0, 0),
        (0, 0, 255),
        (255, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
        (128, 128, 0),
        (0, 128, 128),
        (128, 0, 128),
    ]
    return colors[idx % len(colors)]


# =======================
def process_video(video_path, model_path="yolov8x-pose.pt"):
    # Carrega modelo
    model = YOLO(model_path)

    # Configura entrada e saída de vídeo
    cap, output_video, fps, width, height, total_frames = setup_video_io(video_path)
    progress_bar = tqdm(total=total_frames, desc="Processando", unit="frame")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        progress_bar.update(1)

        # Detecção com tracking
        results = model.track(source=frame, persist=True, classes=0, verbose=False)
        annotated_image = frame.copy()
        person_count = 0

        r = results[0]

        if r.keypoints is not None and r.boxes is not None and r.boxes.id is not None:
            for box, keypoints_tensor, track_id in zip(
                r.boxes.xyxy, r.keypoints.xy, r.boxes.id
            ):
                keypoints = keypoints_tensor.cpu().numpy()

                person_count += 1
                x1, y1, x2, y2 = map(int, box.tolist())
                pid = int(track_id.item()) if track_id is not None else person_count
                color = get_color(pid)

                # Caixa e ID
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated_image,
                    f"ID {pid}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2,
                )

                # Keypoints
                for kp in keypoints:
                    px, py = int(kp[0]), int(kp[1])
                    cv2.circle(annotated_image, (px, py), 3, color, -1)

        # Grava frame
        output_video.write(annotated_image)

        # Mostrar (opcional)
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
    parser = argparse.ArgumentParser(description="Detector de caminhada com YOLO Pose")
    parser.add_argument(
        "video_path", type=str, help="Caminho do arquivo de vídeo a ser processado"
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="yolov8x-pose.pt",
        help="Caminho do modelo YOLOv8 Pose (opcional)",
    )
    args = parser.parse_args()

    process_video(args.video_path, args.model_path)
