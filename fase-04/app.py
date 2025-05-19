import os
import time
import streamlit as st
from detector import detect_emotions
from report import generate_emotion_report, generate_pose_report
from pose_detection import process_video as process_pose_video

st.set_page_config(page_title="Detector de Emoções e Poses com IA")
st.title("🤖 Análise de Vídeo com IA")

VIDEO_DIR = "data"
VIDEO_OUTPUT_DIR = "data/output/"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)
video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]

# Opção entre módulos
option = st.sidebar.radio(
    "Selecione a funcionalidade:", ("Detecção de Emoções", "Detecção de Poses")
)

selected_video = st.selectbox("🎬 Selecione um vídeo:", video_files)

if selected_video:
    input_path = os.path.join(VIDEO_DIR, selected_video)
    st.video(input_path)

    raw_path = os.path.join(VIDEO_DIR, f"raw_{selected_video}")

    if option == "Detecção de Emoções":
        if st.button("🔍 Processar Emoções"):
            st.info("Processando emoções... Isso pode levar alguns minutos.")
            progress_bar = st.progress(0)

            fixed_path = os.path.join(VIDEO_OUTPUT_DIR, f"emotion_{selected_video}")

            total_frames, emotion_counts = detect_emotions(
                input_path,
                raw_path,
                fixed_path,
                progress_callback=progress_bar.progress,
            )
            time.sleep(1)

            if os.path.exists(fixed_path) and os.path.getsize(fixed_path) > 0:
                st.success("✅ Processamento finalizado!")
                st.video(fixed_path)

                report_md = generate_emotion_report(total_frames, emotion_counts)
                st.markdown("---")
                st.markdown(report_md)
            else:
                st.error("❌ O vídeo de saída não pôde ser carregado.")

    elif option == "Detecção de Poses":
        if st.button("🏃 Processar Pose"):
            st.info("Executando detecção de pose...")
            progress_bar = st.progress(0)

            output_path = os.path.join(VIDEO_OUTPUT_DIR, f"pose_{selected_video}")

            total_frames, poses_count = process_pose_video(
                input_path, output_path, progress_callback=progress_bar.progress
            )

            time.sleep(1)
            if os.path.exists(output_path):
                st.success("✅ Processamento de pose finalizado!")
                st.video(output_path)

                report_md = generate_pose_report(total_frames, poses_count)
                st.markdown("---")
                st.markdown(report_md)
            else:
                st.error("❌ Não foi possível gerar o vídeo de saída.")
