import argparse
from moviepy import VideoFileClip


def recortar_video(input_path, output_path, inicio, fim):
    video = VideoFileClip(input_path).subclipped(inicio, fim)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recorta um trecho de um vídeo MP4.")
    parser.add_argument("input", help="Caminho do vídeo de entrada (MP4)")
    parser.add_argument("output", help="Caminho do vídeo de saída (MP4)")
    parser.add_argument("inicio", help="Tempo de início (formato hh:mm:ss ou mm:ss)")
    parser.add_argument("fim", help="Tempo de fim (formato hh:mm:ss ou mm:ss)")

    args = parser.parse_args()

    recortar_video(args.input, args.output, args.inicio, args.fim)
