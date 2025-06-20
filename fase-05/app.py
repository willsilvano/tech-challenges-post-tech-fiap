# app.py
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io
import os
import pandas as pd
from dotenv import load_dotenv
import re

load_dotenv()

# --- Configuração da Página e da API ---
st.set_page_config(
    page_title="Análise de Arquitetura com Gemini", page_icon="🛡️", layout="wide"
)

# Checa se a variável de ambiente GOOGLE_API_KEY está definida
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error(
        "A variável de ambiente GOOGLE_API_KEY não foi encontrada. O aplicativo será encerrado. Por favor, defina a chave antes de executar."
    )
    st.stop()

llm_model = os.getenv("GOOGLE_LLM_MODEL")
if not llm_model:
    st.error(
        "A variável de ambiente GOOGLE_LLM_MODEL não foi encontrada. O aplicativo será encerrado. Por favor, defina o modelo LLM antes de executar."
    )
    st.stop()

# Configurar a API do Gemini a partir dos segredos do Streamlit
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Erro ao configurar a API do Gemini: {e}")
    st.stop()

# --- Funções de Interação com a API ---


def extract_components_from_image(image_bytes):
    """
    Usa o modelo Gemini Vision para extrair componentes da imagem de arquitetura.
    """
    model = genai.GenerativeModel(llm_model)

    # Converte bytes para um objeto de imagem PIL para o modelo
    img = Image.open(io.BytesIO(image_bytes))

    prompt = """
    Analise esta imagem de uma arquitetura de sistema em nuvem.
    Identifique todos os componentes tecnológicos, serviços e recursos (ex: AWS Shield, Application Load Balancer, Amazon RDS, EFS, etc.).
    Liste os componentes extraídos em um formato de lista JSON.
    Exemplo de saída:
    {
      "componentes": [
        "AWS Shield",
        "Amazon CloudFront",
        "AWS WAF",
        "Application Load Balancer",
        "Auto Scaling Group",
        "Servidores de API (SEI/SIP)",
        "Solr",
        "Amazon RDS (PostgreSQL)",
        "Amazon EFS",
        "Amazon ElastiCache"
      ]
    }
    Retorne APENAS o JSON, sem nenhum texto ou formatação adicional.
    """

    try:
        response = model.generate_content([prompt, img])
        # Limpa a resposta para garantir que apenas o JSON seja extraído
        json_text = (
            response.text.strip().replace("```json", "").replace("```", "").strip()
        )
        # Analisa o texto JSON em um dicionário Python
        return json.loads(json_text)
    except Exception as e:
        st.error(f"Erro ao extrair componentes: {e}")
        st.error(
            f"Resposta bruta da API: {response.text if 'response' in locals() else 'Nenhuma resposta recebida'}"
        )
        return None


def get_stride_analysis(components_list):
    """
    Gera uma análise STRIDE detalhada com base em uma lista de componentes.
    """
    model = genai.GenerativeModel(llm_model)

    # Formata a lista de componentes para o prompt
    component_str = ", ".join(components_list)

    prompt = f"""
    Aja como um especialista em segurança de aplicações (AppSec).
    Com base na seguinte lista de componentes de uma arquitetura em nuvem: **{
        component_str
    }**.

    Realize uma análise de ameaças usando a metodologia STRIDE.
    Para cada categoria do STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege), identifique ameaças potenciais relacionadas aos componentes listados e sugira medidas de contorno (mitigações) concretas.

    Retorne um JSON com a seguinte estrutura:

    [
        {{
        "Categoria STRIDE": "Spoofing",
            "Ameaça Potencial": "Um atacante pode se passar por um usuário legítimo",
            "Componentes Afetados": "Servidores de API, Application Load Balancer",
            "Medida de Contorno Sugerida": "Implementar autenticação multifator (MFA) e monitoramento de logs de acesso"
        }}
    ]

    Retorne APENAS o JSON sem nenhum texto ou formatação adicional.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar a análise STRIDE: {e}")
        return None


# --- Interface da Aplicação ---

st.title("🛡️ Análise de Arquitetura e Vulnerabilidades com Gemini")
st.markdown(
    "Faça o upload de uma imagem da sua arquitetura de sistema para que a IA identifique os componentes, analise as vulnerabilidades usando o método STRIDE e sugira mitigações."
)

st.sidebar.header("Como usar:")
st.sidebar.info(
    "1. **Carregue a Imagem**: Use o botão de upload para carregar um diagrama da sua arquitetura.\n\n"
    "2. **Processe a Imagem**: Clique no botão 'Analisar Arquitetura com Gemini'.\n\n"
    "3. **Revise os Relatórios**: A aplicação irá gerar dois relatórios: a lista de componentes extraídos e a análise completa de ameaças STRIDE."
)
st.sidebar.warning(
    "Os resultados são gerados por IA e devem ser revisados por um especialista em segurança. A precisão depende da qualidade e clareza da imagem."
)


# --- Seção de Upload ---
st.header("1. Upload da Modelagem da Arquitetura")
uploaded_file = st.file_uploader(
    "Selecione um arquivo de imagem (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # Converte o arquivo para bytes para envio
    image_bytes = uploaded_file.getvalue()

    st.image(
        image_bytes, caption="Imagem da Arquitetura Carregada", use_container_width=True
    )

    if st.button("🚀 Analisar Arquitetura com Gemini", type="primary"):
        st.session_state.components_result = None
        st.session_state.stride_result = None

        # Etapa 1: Extrair Componentes
        with st.spinner("Etapa 1/2: Analisando a imagem para extrair componentes..."):
            components_result = extract_components_from_image(image_bytes)
            st.session_state.components_result = components_result

        if (
            st.session_state.components_result
            and "componentes" in st.session_state.components_result
        ):
            st.subheader("Componentes Identificados pela IA:")
            extracted_components = st.session_state.components_result["componentes"]

            df_componentes = pd.DataFrame({"Componente": extracted_components})
            st.dataframe(df_componentes, hide_index=True)

            # Etapa 2: Gerar Análise STRIDE
            with st.spinner("Etapa 2/2: Gerando relatório de ameaças STRIDE..."):
                stride_result = get_stride_analysis(extracted_components)
                try:
                    # Limpa a resposta para garantir que apenas o JSON seja extraído
                    stride_json_text = (
                        stride_result.strip()
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    stride_json = json.loads(stride_json_text)
                    df_stride = pd.DataFrame(stride_json)
                    st.subheader("Análise STRIDE feita pela IA:")
                    st.dataframe(
                        df_stride,
                        hide_index=True,
                        use_container_width=True,
                    )
                    st.toast("Análise concluída com sucesso!", icon="✅")
                except Exception as e:
                    st.session_state.stride_json = None
                    st.error(f"Erro ao processar o JSON da análise STRIDE: {e}")
                    st.error(f"Resposta bruta da API: {stride_result}")
        else:
            st.error(
                "Não foi possível extrair componentes da imagem. Tente uma imagem mais clara ou com componentes mais definidos."
            )
