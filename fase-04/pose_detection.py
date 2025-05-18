import argparse
import math
import cv2
from tqdm import tqdm
from ultralytics import YOLO
import numpy as np
import os
from typing import List, Tuple, Optional, Dict, Any
from detector import fix_video_codec

LANDMARK_NAMES: List[str] = [
    "nariz",
    "olho_esquerdo",
    "olho_direito",
    "orelha_esquerda",
    "orelha_direita",
    "ombro_esquerdo",
    "ombro_direito",
    "cotovelo_esquerdo",
    "cotovelo_direito",
    "pulso_esquerdo",
    "pulso_direito",
    "quadril_esquerdo",
    "quadril_direito",
    "joelho_esquerdo",
    "joelho_direito",
    "tornozelo_esquerdo",
    "tornozelo_direito",
]

# =======================
# Constantes de Landmarks (Índices)
# =======================
NARIZ = 0
OLHO_ESQUERDO = 1
OLHO_DIREITO = 2
ORELHA_ESQUERDA = 3
ORELHA_DIREITA = 4
OMBRO_ESQUERDO = 5
OMBRO_DIREITO = 6
COTOVELO_ESQUERDO = 7
COTOVELO_DIREITO = 8
PULSO_ESQUERDO = 9
PULSO_DIREITO = 10
QUADRIL_ESQUERDO = 11
QUADRIL_DIREITO = 12
JOELHO_ESQUERDO = 13
JOELHO_DIREITO = 14
TORNOZELO_ESQUERDO = 15
TORNOZELO_DIREITO = 16

# Mapa de nome para índice para facilitar o parsing de argumentos e referência
LANDMARK_NAME_TO_INDEX_MAP: Dict[str, int] = {
    name: i for i, name in enumerate(LANDMARK_NAMES)
}


# =======================
# Funções utilitárias
# =======================
def setup_video_io(
    video_path: str
) -> Tuple[cv2.VideoCapture, cv2.VideoWriter, str, int, int, int, int]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Não foi possível abrir o vídeo: {video_path}")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    base, ext = os.path.splitext(video_path)
    output_path = f"{base}_output{ext}"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    return cap, output_video, output_path, fps, width, height, total_frames


def get_color(idx: int) -> Tuple[int, int, int]:
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
        (128, 128, 128),
        (64, 0, 0),
        (0, 64, 0),
        (0, 0, 64),
        (64, 64, 0),
        (0, 64, 64),
        (64, 0, 64),
    ]
    return colors[idx % len(colors)]


def distance_between_points(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def height_between_points(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return abs(p1[1] - p2[1])


def is_looking_down(
    keypoints: np.ndarray,
    angle_threshold: float = 28.0,
    annotated_image: Optional[np.ndarray] = None,
) -> bool:
    """
    Verifica se a pessoa está olhando para baixo com base no ângulo entre nariz e orelha.
    Se annotated_image for fornecida, desenha o debug.

    :param keypoints: Array de keypoints (N x 2)
    :param angle_threshold: Ângulo mínimo (em graus) para considerar como "olhando para baixo"
    :param annotated_image: Imagem para desenhar debug (opcional)
    :return: True se estiver olhando para baixo
    """
    nariz = keypoints[NARIZ]
    orelha_dir = keypoints[ORELHA_DIREITA]
    orelha_esq = keypoints[ORELHA_ESQUERDA]

    def is_valid(p):
        return not np.any(np.isnan(p)) and not np.all(p == 0)

    # Usa a orelha visível (preferência para direita)
    if is_valid(orelha_dir):
        orelha = orelha_dir
    elif is_valid(orelha_esq):
        orelha = orelha_esq
    else:
        return False  # Nenhuma orelha válida

    dx = nariz[0] - orelha[0]
    dy = nariz[1] - orelha[1]

    if dx == 0 and dy == 0:
        return False

    angle_rad = math.atan2(dy, dx)
    angle_deg = abs(math.degrees(angle_rad))
    olhando_baixo = angle_deg > angle_threshold

    return olhando_baixo


def is_hand_raised(keypoints: np.ndarray, lado: str = "direito") -> bool:
    """
    Verifica se a mão está levantada com base na posição vertical do pulso em relação ao ombro.

    :param keypoints: Array dos keypoints (N x 2)
    :param lado: "direito" ou "esquerdo"
    :return: True se a mão do lado especificado estiver levantada
    """
    if lado == "direito":
        ombro = keypoints[OMBRO_DIREITO]
        cotovelo = keypoints[COTOVELO_DIREITO]
        pulso = keypoints[PULSO_DIREITO]
    elif lado == "esquerdo":
        ombro = keypoints[OMBRO_ESQUERDO]
        cotovelo = keypoints[COTOVELO_ESQUERDO]
        pulso = keypoints[PULSO_ESQUERDO]
    else:
        raise ValueError("Lado deve ser 'direito' ou 'esquerdo'.")

    # Verificação de validade
    def is_valid(p):
        return not np.any(np.isnan(p)) and not np.all(p == 0)

    if not (is_valid(ombro) and is_valid(cotovelo) and is_valid(pulso)):
        return False

    # Critério 1: pulso acima do ombro
    if pulso[1] < ombro[1]:
        return True

    return False


def is_hand_on_face_by_region(
    keypoints: np.ndarray,
    annotated_image: Optional[np.ndarray] = None,
    margin_y: int = 30,
) -> bool:
    """
    Verifica se o pulso está dentro da área vertical do rosto (com margem aplicada apenas verticalmente).

    :param keypoints: Array de keypoints (N x 2)
    :param annotated_image: Imagem para visualização (opcional)
    :param margin_y: Margem aplicada somente no eixo Y (vertical)
    :return: True se a mão estiver dentro da área facial
    """
    face_indices = [NARIZ, OLHO_DIREITO, OLHO_ESQUERDO, ORELHA_DIREITA, ORELHA_ESQUERDA]
    valid_face_pts = [
        keypoints[i]
        for i in face_indices
        if not np.any(np.isnan(keypoints[i])) and not np.all(keypoints[i] == 0)
    ]

    if len(valid_face_pts) < 3:
        return False

    face_pts = np.array(valid_face_pts, dtype=np.int32)
    x, y, w, h = cv2.boundingRect(face_pts)

    # Aplicar margem apenas verticalmente
    y -= margin_y
    h += 2 * margin_y

    pulso_dir = keypoints[PULSO_DIREITO]
    pulso_esq = keypoints[PULSO_ESQUERDO]

    def is_inside_face(p):
        if np.any(np.isnan(p)) or np.all(p == 0):
            return False
        return x <= p[0] <= x + w and y <= p[1] <= y + h

    return is_inside_face(pulso_dir) or is_inside_face(pulso_esq)


def draw_action_text(
    annotated_image: np.ndarray,
    keypoints: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> None:
    olhando_baixo = is_looking_down(keypoints)
    mao_levantada = is_hand_raised(keypoints, "direito") or is_hand_raised(
        keypoints, "esquerdo"
    )
    mao_no_rosto = is_hand_on_face_by_region(keypoints, annotated_image, margin_y=250)

    if mao_no_rosto:
        action = "Mao no rosto"
    elif olhando_baixo:
        action = "Olhar inclinado"
    elif mao_levantada:
        action = "Mao levantada"
    else:
        action = "Desconhecida"

    text_size, _ = cv2.getTextSize(action, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    text_width, text_height = text_size

    text_x = x1 + 5
    text_y_bottom = y2 - 10
    text_y_top = y1 + text_height + 10

    if text_y_bottom - text_height > y1:
        text_y = text_y_bottom
        bg_rect_y1, bg_rect_y2 = text_y - text_height - 2, text_y + 4
    else:
        text_y = text_y_top
        bg_rect_y1, bg_rect_y2 = y1 + 5, y1 + 5 + text_height + 6

    cv2.rectangle(
        annotated_image,
        (text_x - 2, bg_rect_y1),
        (text_x + text_width + 2, bg_rect_y2),
        (0, 0, 255) if action == "Desconhecida" else (255, 0, 0),
        -1,
    )
    cv2.putText(
        annotated_image,
        action,
        (text_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )


def draw_person_annotations(
    annotated_image: np.ndarray,
    box: List[float],
    keypoints: np.ndarray,
    track_id: Optional[int],
    color: Tuple[int, int, int],
    monitor_landmarks_indices: List[int],
) -> None:
    """Desenha anotações para uma única pessoa detectada."""
    x1, y1, x2, y2 = map(int, box)

    # Caixa e ID (se disponível)
    cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
    if track_id is not None:
        id_text_y = (
            y1 - 10 if y1 - 10 > 10 else y1 + 20
        )  # Adjusted y1+10 to y1+20 for better visibility
        cv2.putText(
            annotated_image,
            f"ID {track_id}",
            (x1, id_text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )

    # Texto da ação
    draw_action_text(annotated_image, keypoints, x1, y1, x2, y2)

    # Keypoints
    for lm_idx, kp in enumerate(keypoints):
        if lm_idx not in monitor_landmarks_indices:
            continue

        px, py = int(kp[0]), int(kp[1])
        if px == 0 and py == 0:  # Pular keypoints não detectados
            continue

        cv2.circle(annotated_image, (px, py), 3, color, -1)
        landmark_name = LANDMARK_NAMES[lm_idx]
        cv2.putText(
            annotated_image,
            landmark_name,
            (px + 5, py - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            color,
            1,
        )


# =======================
# Função principal de processamento
# =======================
def process_video(
    video_path: str,
    output_fixed_path: str,
    model_path: str = "yolov8x-pose.pt",
    person_id_to_monitor: Optional[int] = None,
    monitor_landmarks_indices: Optional[List[int]] = None,
) -> None:
    model = YOLO(model_path)
    cap, output_video, output_path, _, _, _, total_frames = setup_video_io(video_path)

    if monitor_landmarks_indices is None:
        monitor_landmarks_indices = list(range(len(LANDMARK_NAMES)))

    with tqdm(total=total_frames, desc="Processando", unit="frame") as progress_bar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            progress_bar.update(1)
            annotated_image = frame.copy()

            results = model.track(
                source=frame,
                persist=True,
                classes=0,
                verbose=False,
                tracker="bytetrack.yaml",
            )

            if (
                results
                and results[0].boxes is not None
                and results[0].keypoints is not None
            ):
                r = results[0]
                boxes_data = r.boxes.xyxy.cpu().numpy()  # Ensure it's numpy
                keypoints_data = r.keypoints.xy.cpu().numpy()  # Ensure it's numpy
                track_ids_tensor = r.boxes.id

                num_detections = len(boxes_data)
                track_ids = (
                    track_ids_tensor.cpu().numpy().astype(int)
                    if track_ids_tensor is not None
                    else [None] * num_detections
                )

                for i in range(num_detections):
                    box = boxes_data[i]
                    keypoints = keypoints_data[i]
                    current_track_id = (
                        track_ids[i] if track_ids_tensor is not None else None
                    )

                    if (
                        person_id_to_monitor is not None
                        and current_track_id != person_id_to_monitor
                    ):
                        continue

                    # Use track_id for color if available, otherwise use detection index
                    color_idx = current_track_id if current_track_id is not None else i
                    color = get_color(color_idx)

                    draw_person_annotations(
                        annotated_image,
                        box,
                        keypoints,
                        current_track_id,
                        color,
                        monitor_landmarks_indices,
                    )

            output_video.write(annotated_image)
            cv2.imshow("Tracking com Pose", annotated_image)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
                break

    cap.release()
    output_video.release()
    cv2.destroyAllWindows()

    fix_video_codec(output_path, output_fixed_path)

    print("Processamento finalizado com sucesso!")


# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Detector de pose e tracking com YOLOv8 Pose"
    )
    parser.add_argument(
        "--video_path",
        type=str,
        required=True,
        help="Caminho do arquivo de vídeo a ser processado.",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="yolov8x-pose.pt",
        help="Caminho do modelo YOLOv8 Pose (opcional).",
    )
    parser.add_argument(
        "--person_id",
        type=int,
        default=None,
        help="ID da pessoa para monitorar especificamente. Se não fornecido, monitora todas.",
    )
    # Adicionar argumento para landmarks específicos (opcional, mas bom para flexibilidade)
    parser.add_argument(
        "--monitor_landmarks_names",
        nargs="+",
        type=str,
        default=None,
        choices=LANDMARK_NAMES,
        help=f"Nomes dos landmarks para monitorar (ex: nariz ombro_esquerdo). Padrão: todos. Escolhas: {', '.join(LANDMARK_NAMES)}",
    )

    args = parser.parse_args()

    selected_landmark_indices: Optional[List[int]] = None
    if args.monitor_landmarks_names:
        selected_landmark_indices = [
            LANDMARK_NAME_TO_INDEX_MAP[name] for name in args.monitor_landmarks_names
        ]
    else:  # Default to all landmarks if none are specified
        selected_landmark_indices = list(range(len(LANDMARK_NAMES)))

    process_video(
        args.video_path, args.model_path, args.person_id, selected_landmark_indices
    )
