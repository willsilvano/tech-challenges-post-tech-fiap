# app.py
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io
import os

from dotenv import load_dotenv

load_dotenv()

# --- Configuração da Página e da API ---
st.set_page_config(
    page_title="Análise de Arquitetura com Gemini",
    page_icon="🛡️",
    layout="wide"
)

# Configurar a API do Gemini a partir dos segredos do Streamlit
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
except (KeyError, FileNotFoundError):
    st.error("A chave de API do Google não foi encontrada. Por favor, adicione-a em .streamlit/secrets.toml.")
    st.stop()

# --- Funções de Interação com a API ---

def extract_components_from_image(image_bytes):
    """
    Usa o modelo Gemini Vision para extrair componentes da imagem de arquitetura.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
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
        json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        # Analisa o texto JSON em um dicionário Python
        return json.loads(json_text)
    except Exception as e:
        st.error(f"Erro ao extrair componentes: {e}")
        st.error(f"Resposta bruta da API: {response.text if 'response' in locals() else 'Nenhuma resposta recebida'}")
        return None

def get_stride_analysis(components_list):
    """
    Gera uma análise STRIDE detalhada com base em uma lista de componentes.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest') # Usando um modelo mais rápido para análise de texto
    
    # Formata a lista de componentes para o prompt
    component_str = ", ".join(components_list)
    
    prompt = f"""
    Aja como um especialista em segurança de aplicações (AppSec).
    Com base na seguinte lista de componentes de uma arquitetura em nuvem: **{component_str}**.

    Realize uma análise de ameaças usando a metodologia STRIDE.
    Para cada categoria do STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege), identifique ameaças potenciais relacionadas aos componentes listados e sugira medidas de contorno (mitigações) concretas.

    Formate a saída como uma tabela Markdown com as seguintes colunas:
    'Categoria STRIDE', 'Ameaça Potencial', 'Componentes Afetados', 'Medida de Contorno Sugerida'.

    Exemplo de linha:
    | Spoofing | Falsificação de identidade de usuários ou serviços para acessar APIs. | API Servers, Solr, RDS | Implementar autenticação forte (OAuth2, mTLS) e controle de acesso granular com IAM Roles. |

    Apresente a análise completa na tabela Markdown.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar a análise STRIDE: {e}")
        return None

# --- Interface da Aplicação ---

st.title("🛡️ Análise de Arquitetura e Vulnerabilidades com Gemini")
st.markdown("Faça o upload de uma imagem da sua arquitetura de sistema para que a IA identifique os componentes, analise as vulnerabilidades usando o método STRIDE e sugira mitigações.")

st.sidebar.header("Como usar:")
st.sidebar.info(
    "1. **Carregue a Imagem**: Use o botão de upload para carregar um diagrama da sua arquitetura.\n\n"
    "2. **Processe a Imagem**: Clique no botão 'Analisar Arquitetura com Gemini'.\n\n"
    "3. **Revise os Relatórios**: A aplicação irá gerar dois relatórios: a lista de componentes extraídos e a análise completa de ameaças STRIDE."
)
st.sidebar.warning("Os resultados são gerados por IA e devem ser revisados por um especialista em segurança. A precisão depende da qualidade e clareza da imagem.")


# --- Seção de Upload ---
st.header("1. Upload da Modelagem da Arquitetura")
uploaded_file = st.file_uploader(
    "Selecione um arquivo de imagem (.png, .jpg, .jpeg)",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # Converte o arquivo para bytes para envio
    image_bytes = uploaded_file.getvalue()
    
    st.image(image_bytes, caption="Imagem da Arquitetura Carregada", use_column_width=True)

    if st.button("🚀 Analisar Arquitetura com Gemini", type="primary"):
        st.session_state.components_result = None
        st.session_state.stride_result = None

        # Etapa 1: Extrair Componentes
        with st.spinner("Etapa 1/2: Analisando a imagem para extrair componentes..."):
            components_result = extract_components_from_image(image_bytes)
            st.session_state.components_result = components_result

        if st.session_state.components_result and 'componentes' in st.session_state.components_result:
            st.subheader("Componentes Identificados pela IA:")
            extracted_components = st.session_state.components_result['componentes']
            st.info(f"**Componentes:** {', '.join(extracted_components)}")

            # Etapa 2: Gerar Análise STRIDE
            with st.spinner("Etapa 2/2: Gerando relatório de ameaças STRIDE..."):
                stride_result = get_stride_analysis(extracted_components)
                st.session_state.stride_result = stride_result
        else:
            st.error("Não foi possível extrair componentes da imagem. Tente uma imagem mais clara ou com componentes mais definidos.")

# --- Exibição dos Resultados ---
if 'stride_result' in st.session_state and st.session_state.stride_result:
    st.header("Relatório de Análise de Ameaças (STRIDE)")
    st.markdown(st.session_state.stride_result)
    st.success("Análise concluída com sucesso!")
    st.balloons()