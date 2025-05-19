import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


def generate_emotion_report(total_frames, emotion_counts):
    total_detected = sum(emotion_counts.values())
    top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)

    report_lines = [
        f"📝 **Relatório de Análise de Emoções**",
        f"- Total de frames analisados: {total_frames}",
        f"- Emoções mais frequentes:",
    ]
    for emotion, count in top_emotions:
        report_lines.append(f"    - {emotion}: {count} ocorrência(s)")

    report_md = "\n".join(report_lines)

    # Exibir gráfico de barras
    if emotion_counts:
        df = pd.DataFrame(top_emotions, columns=["Emoção", "Ocorrências"])
        st.markdown("### 📊 Distribuição das Emoções Detectadas")
        fig, ax = plt.subplots()
        sns.barplot(data=df, x="Emoção", y="Ocorrências", ax=ax, palette="pastel")
        ax.set_ylabel("Ocorrências")
        ax.set_title("Frequência das Emoções Detectadas")
        st.pyplot(fig)

    return report_md


def generate_pose_report(total_frames, poses_count):
    report_lines = [
        f"📝 **Relatório de Análise de Poses**",
        f"- Total de frames analisados: {total_frames}",
        f"- Poses mais frequentes:",
    ]
    for pose, count in poses_count.items():
        report_lines.append(f"    - {pose}: {count} ocorrência(s)")

    report_md = "\n".join(report_lines)

    # Exibir gráfico de barras
    if poses_count:
        df = pd.DataFrame(poses_count.items(), columns=["Pose", "Ocorrências"])
        st.markdown("### 📊 Distribuição das Poses Detectadas")
        fig, ax = plt.subplots()
        sns.barplot(data=df, x="Pose", y="Ocorrências", ax=ax, palette="pastel")
        ax.set_ylabel("Ocorrências")
        ax.set_title("Frequência das Poses Detectadas")
        st.pyplot(fig)

    return report_md
