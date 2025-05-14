import cv2
import mediapipe as mp
from tqdm import tqdm
from ultralytics import YOLO  # YOLOv8 para detecção de múltiplas pessoas

# Configurações do MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Para detecção de pessoas, usamos YOLOv8 que é melhor para múltiplas pessoas
model = YOLO("yolov8x.pt")  # Download automático do modelo na primeira execução

# Inicializa o estimador de pose
pose = mp_pose.Pose(
    static_image_mode=True,  # Usamos static_image_mode=True para processar cada recorte independentemente
    model_complexity=1,
    enable_segmentation=False,  # Desativamos segmentação para manter o background original
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Caminho do arquivo de vídeo
video_path = "fase-04/data/walk.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Erro ao abrir o vídeo: {video_path}")
    exit()

# Obtém propriedades do vídeo
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Configura o VideoWriter para salvar o vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # codec
output_video = cv2.VideoWriter(f"data/output-{video_path}.mp4", fourcc, fps, (width, height))

# Cria barra de progresso com tqdm
progress_bar = tqdm(total=total_frames, desc="Processando frames", unit="frame")

# Para armazenar cores de diferentes pessoas
colors = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
]

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # terminou o vídeo

    frame_count += 1
    progress_bar.update(1)

    # Cria uma cópia do frame para anotações, mantendo o background original
    annotated_image = frame.copy()

    # 1. Detecta pessoas com YOLOv8
    yolo_results = model(frame, classes=0)  # classe 0 = pessoa no YOLOv8

    # 2. Para cada pessoa detectada
    person_count = 0
    for i, det in enumerate(yolo_results[0].boxes):
        if det.cls == 0:  # Classe "pessoa"
            person_count += 1
            box = det.xyxy[0].cpu().numpy().astype(int)  # Converte para inteiros
            x1, y1, x2, y2 = box

            # Adiciona uma pequena margem ao recorte
            margin = 10
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(width, x2 + margin)
            y2 = min(height, y2 + margin)

            # Recorta a região da pessoa
            person_roi = frame[y1:y2, x1:x2]

            if person_roi.size == 0:
                continue  # Skip se o ROI for vazio

            # Converte para RGB (MediaPipe requer RGB)
            roi_rgb = cv2.cvtColor(person_roi, cv2.COLOR_BGR2RGB)

            # Processa a região com MediaPipe Pose
            results = pose.process(roi_rgb)

            # Escolhe uma cor para esta pessoa
            color_idx = person_count % len(colors)
            person_color = colors[color_idx]

            # Desenha a caixa da pessoa
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), person_color, 2)

            # Adiciona ID da pessoa
            cv2.putText(
                annotated_image,
                f"Pessoa #{person_count}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                person_color,
                2,
            )

            # Se landmarks da pose foram detectados
            if results.pose_landmarks:
                # Converte landmarks para coordenadas absolutas no frame original
                h_roi, w_roi = person_roi.shape[:2]

                # Desenha os landmarks da pose no frame original
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    # Converte coordenadas relativas ao ROI para coordenadas absolutas do frame
                    px = int(landmark.x * w_roi) + x1
                    py = int(landmark.y * h_roi) + y1

                    # Desenha círculo para cada landmark
                    cv2.circle(annotated_image, (px, py), 3, person_color, -1)

                    # Opcionalmente, desenha o número do landmark
                    if landmark.visibility > 0.5:
                        cv2.putText(
                            annotated_image,
                            str(idx),
                            (px, py),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1,
                        )

                # Desenha as conexões entre landmarks (esqueleto)
                # Conexões principais do corpo
                connections = [
                    # Tronco
                    (11, 12),
                    (12, 24),
                    (24, 23),
                    (23, 11),
                    # Braço direito
                    (12, 14),
                    (14, 16),
                    # Braço esquerdo
                    (11, 13),
                    (13, 15),
                    # Perna direita
                    (24, 26),
                    (26, 28),
                    # Perna esquerda
                    (23, 25),
                    (25, 27),
                    # Cabeça
                    (11, 12),
                    (12, 0),
                    (0, 11),
                ]

                for connection in connections:
                    start_idx, end_idx = connection
                    if (
                        results.pose_landmarks.landmark[start_idx].visibility > 0.5
                        and results.pose_landmarks.landmark[end_idx].visibility > 0.5
                    ):
                        start_point = (
                            int(results.pose_landmarks.landmark[start_idx].x * w_roi)
                            + x1,
                            int(results.pose_landmarks.landmark[start_idx].y * h_roi)
                            + y1,
                        )
                        end_point = (
                            int(results.pose_landmarks.landmark[end_idx].x * w_roi)
                            + x1,
                            int(results.pose_landmarks.landmark[end_idx].y * h_roi)
                            + y1,
                        )

                        cv2.line(
                            annotated_image, start_point, end_point, person_color, 2
                        )

    # Adiciona contador de pessoas no canto superior
    cv2.putText(
        annotated_image,
        f"Total: {person_count} pessoas",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    # Salva o frame processado no vídeo de saída
    output_video.write(annotated_image)


# Fechando a barra de progresso
progress_bar.close()

# Libera recursos
cap.release()
output_video.release()
cv2.destroyAllWindows()

print("Vídeo processado com sucesso! Salvo como 'output.mp4'")
print(f"Total de frames processados: {frame_count}")
print(f"Última contagem de pessoas: {person_count}")
