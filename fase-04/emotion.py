import os

import cv2
import mediapipe as mp
import tensorflow as tf
from deepface import DeepFace
from tqdm import tqdm

# --- Configuração para forçar o TensorFlow a usar a CPU ---
# Isso ajuda a evitar erros relacionados à GPU/CUDA/CuDNN incompatíveis
try:
    # Obter a lista de GPUs disponíveis
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        # Se houver GPUs, desabilitá-las explicitamente
        try:
            for gpu in gpus:
                tf.config.set_visible_devices([], 'GPU')  # Define a lista de GPUs visíveis como vazia
            logical_gpus = tf.config.list_logical_devices('GPU')
            print(f"GPUs físicas: {len(gpus)} | GPUs lógicas visíveis: {len(logical_gpus)}")
            if len(logical_gpus) == 0:
                print("GPUs desabilitadas com sucesso. TensorFlow usará a CPU.")
            else:
                print("Aviso: Não foi possível desabilitar todas as GPUs lógicas.")
        except RuntimeError as e:
            # Capturar erro se a configuração for chamada após a inicialização do dispositivo
            print(f"Erro ao configurar GPUs para desabilitar: {e}")
    else:
        print("Nenhuma GPU encontrada. TensorFlow usará a CPU por padrão.")
except Exception as e:
    print(f"Erro ao verificar ou configurar GPUs: {e}")
# --- Fim da configuração para CPU ---


# Desabilitar CUDA para DeepFace se necessário, como no código original
# Embora a configuração acima já force a CPU, manter esta linha não prejudica
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def detect_emotions_with_mediapipe(video_path, output_path):
    """
    Detecta emoções em um vídeo usando MediaPipe para detecção facial
    e DeepFace para análise de emoção.

    Args:
        video_path (str): Caminho para o arquivo de vídeo de entrada.
        output_path (str): Caminho para salvar o arquivo de vídeo de saída.
    """
    # Inicializar MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    # mp_drawing = mp.solutions.drawing_utils # Não usaremos mp_drawing para desenhar o bbox, faremos manualmente

    # Configurar o detector de rosto do MediaPipe. min_detection_confidence pode ser ajustado.
    # Ajustei o modelo para 1 para melhor precisão em vídeos, pode ser 0 para detecção mais rápida.
    face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.7)

    # Abrir o arquivo de vídeo
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Erro ao abrir o arquivo de vídeo: {video_path}")
        return

    # Obter propriedades do vídeo
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Configurar o gravador de vídeo de saída
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para .mp4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Processando vídeo: {video_path}")

    # Loop pelos frames do vídeo
    # Usei enumerate para ter o índice do frame, útil para debug se necessário
    for frame_idx in tqdm(range(total_frames), desc="Processando frames"):
        ret, frame = cap.read()

        if not ret:
            # Se não conseguir ler o frame, sai do loop
            print(f"Não foi possível ler o frame {frame_idx}. Fim do vídeo ou erro.")
            break

        # Converter o frame para RGB, que é o formato esperado pelo MediaPipe
        # O DeepFace espera BGR, então voltaremos para BGR antes de desenhar
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processar o frame com o MediaPipe Face Detection
        results = face_detection.process(frame_rgb)

        # Desenhar as detecções faciais e analisar emoções se rostos forem encontrados
        if results.detections:
            for detection in results.detections:
                # Obter as coordenadas do bounding box do MediaPipe
                bbox_c = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bbox_c.xmin * iw), int(bbox_c.ymin * ih), \
                    int(bbox_c.width * iw), int(bbox_c.height * ih)

                # Garantir que as coordenadas estão dentro dos limites do frame
                x = max(0, x)
                y = max(0, y)
                w = min(width - x, w)
                h = min(height - y, h)

                # Extrair a região do rosto
                face_img = frame[y:y + h, x:x + w]

                # Verificar se a região do rosto não está vazia e tem tamanho suficiente para análise
                if face_img.shape[0] > 50 and face_img.shape[1] > 50:  # Adicionado um tamanho mínimo
                    try:
                        # Analisar a emoção usando DeepFace na região do rosto detectada pelo MediaPipe
                        # enforce_detection=False é usado aqui porque o MediaPipe já detectou o rosto
                        # Removido 'prog_bar=False' pois pode não ser suportado em algumas versões do DeepFace
                        analyze_results = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)

                        # DeepFace.analyze retorna uma lista de resultados.
                        # Verificamos se a lista não está vazia e se o resultado tem a chave 'dominant_emotion'
                        if analyze_results and 'dominant_emotion' in analyze_results[0]:
                            dominant_emotion = analyze_results[0]['dominant_emotion']

                            # Desenhar o bounding box no frame original (BGR)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Cor verde, espessura 2

                            # Colocar o texto da emoção acima do bounding box
                            # Ajustar a posição do texto para evitar que fique fora da tela
                            text = dominant_emotion
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 1.0  # Aumentado o tamanho da fonte
                            thickness = 2  # Aumentado a espessura da linha
                            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
                            text_x = x
                            text_y = y - 10 if y - 10 > text_size[1] else y + h + text_size[1]

                            # Desenhar o texto com cor branca para melhor visibilidade
                            cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness,
                                        cv2.LINE_AA)  # Cor branca

                        else:
                            # Se DeepFace não retornar resultados válidos, desenhamos um bounding box vermelho
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255),
                                          2)  # Cor vermelha para indicar que a emoção não foi detectada/analisada
                            # print(f"DeepFace não retornou emoção para o rosto no frame {frame_idx} em ({x},{y})") # Opcional: descomente para debug

                    except Exception as e:
                        # Tratar possíveis erros durante a análise do DeepFace (ex: rosto muito pequeno, erro interno)
                        print(f"Erro ao analisar emoção com DeepFace no frame {frame_idx} em ({x},{y}): {e}")
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Cor vermelha para indicar erro
                else:
                    # Se a região do rosto for inválida ou muito pequena, desenhamos um bounding box vermelho
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Cor vermelha
                    # print(f"Região do rosto inválida ou muito pequena no frame {frame_idx} em ({x},{y}). Tamanho: ({face_img.shape[1]}x{face_img.shape[0]})") # Opcional: descomente para debug

        # Escrever o frame processado no vídeo de saída
        out.write(frame)

    # Liberar os recursos
    cap.release()
    out.release()
    face_detection.close()  # Fechar o detector do MediaPipe
    cv2.destroyAllWindows()

    print(f"Processamento concluído. Vídeo salvo em: {output_path}")


if __name__ == '__main__':
    # Definir os caminhos de entrada e saída
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Certifique-se de que o diretório 'data' existe e o vídeo está lá
    # Mudei o nome do arquivo de entrada para o que você usou no seu teste
    input_video_path = os.path.join(script_dir, 'data', 'video.mp4')
    output_video_path = os.path.join(script_dir, 'data', 'output-emotion.mp4')  # Nome de saída diferente

    # Criar o diretório 'data' se não existir
    output_dir = os.path.join(script_dir, 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Diretório '{output_dir}' criado.")

    # Chamar a função para detectar emoções
    detect_emotions_with_mediapipe(input_video_path, output_video_path)
