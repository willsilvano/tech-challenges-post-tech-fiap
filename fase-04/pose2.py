import cv2
from tqdm import tqdm
from ultralytics import YOLO

# Carrega o modelo de pose com tracking
model = YOLO("yolov8x-pose.pt")

# Vídeo de entrada
video_path = "fase-04/data/persons.mp4"
cap = cv2.VideoCapture(video_path)

# Propriedades do vídeo
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Saída de vídeo
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
output_video = cv2.VideoWriter(f"data/output-{video_path}", fourcc, fps, (width, height))

# Cores para pessoas rastreadas
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

# Barra de progresso
progress_bar = tqdm(total=total_frames, desc="Processando", unit="frame")
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    progress_bar.update(1)

    # Usa o tracking do YOLOv8 (com persistência de IDs)
    results = model.track(source=frame, persist=True, classes=0)

    annotated_image = frame.copy()
    person_count = 0

    if results[0].keypoints is not None:
        for box, keypoints, track_id in zip(
            results[0].boxes.xyxy, results[0].keypoints.xy, results[0].boxes.id
        ):
            person_count += 1
            x1, y1, x2, y2 = map(int, box.tolist())
            pid = int(track_id.item()) if track_id is not None else person_count
            color = colors[pid % len(colors)]

            # Desenha a caixa e ID
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

            # Desenha os pontos-chave
            for kp in keypoints:
                px, py = int(kp[0]), int(kp[1])
                cv2.circle(annotated_image, (px, py), 3, color, -1)

    # Total no canto superior
    cv2.putText(
        annotated_image,
        f"Total: {person_count} pessoas",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    # Salva frame anotado
    output_video.write(annotated_image)

    # Mostra o frame (opcional)
    cv2.imshow("Tracking com Pose", annotated_image)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Finalização
progress_bar.close()
cap.release()
output_video.release()
cv2.destroyAllWindows()
print("Processamento finalizado com sucesso!")
