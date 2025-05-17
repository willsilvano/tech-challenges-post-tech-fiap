import os
import time
import streamlit as st
from detector import detect_emotions
from report import generate_report

# Interface Streamlit
st.set_page_config(page_title="Detector de Emoções com IA")
st.title("🎭 Detector de Emoções em Vídeos")

# Seleção de vídeo
VIDEO_DIR = "data"
VIDEO_OUTPUT_DIR = "data/output/"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)
video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]
selected_video = st.selectbox("🎬 Selecione um vídeo:", video_files)

if selected_video:
    input_path = os.path.join(VIDEO_DIR, selected_video)
    raw_path = os.path.join(VIDEO_DIR, f"raw_{selected_video}")
    fixed_path = os.path.join(VIDEO_OUTPUT_DIR, f"{selected_video}")

    st.video(input_path)

    if st.button("🔍 Processar vídeo"):
        st.info("Processando... Isso pode levar alguns minutos.")
        progress_bar = st.progress(0)

        total_frames, emotion_counts = detect_emotions(input_path, raw_path, fixed_path, progress_callback=progress_bar.progress)
        time.sleep(1)

        if os.path.exists(fixed_path) and os.path.getsize(fixed_path) > 0:
            st.success("✅ Processamento finalizado!")
            st.video(fixed_path)

            # Gerar relatório
            report_md = generate_report(total_frames, emotion_counts)
            st.markdown("---")
            st.markdown(report_md)
        else:
            st.error("❌ O vídeo de saída não pôde ser carregado.")
