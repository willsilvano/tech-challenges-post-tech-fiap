import streamlit as st
import pandas as pd
import os
import time
from typing import List, Dict, Any, Tuple, Optional
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Configurações padrões
MODEL = "llama3.1:8b"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_STORE_PATH = "fase-03/vector_store"
DATA_FILE = "fase-03/data/data-1000.csv"
SIMILARITY_THRESHOLD = 25  # Limiar de similaridade em porcentagem


class ProductAssistant:
    def __init__(
        self,
        llm_model: str = MODEL,
        embedding_model_name: str = EMBEDDING_MODEL,
        vector_store_path: str = VECTOR_STORE_PATH,
        temperature: float = 0.5,
    ):
        """Inicializa o assistente de produtos com os modelos e configurações especificados."""
        self.vector_store_path = vector_store_path
        self.embedding_model = OllamaEmbeddings(model=embedding_model_name)
        self.llm = ChatOpenAI(
            temperature=temperature,
            model=llm_model,
            verbose=True,
            base_url="http://127.0.0.1:1234/v1",
            api_key="123",
        )

        # Verifica se o vetor de armazenamento já existe
        self.vector_store = (
            self._load_vector_store() if os.path.exists(vector_store_path) else None
        )

        # Template do prompt
        self.system_prompt = """
        You are a chatbot that answers questions about products on a Market Store.

        You are a strict assistant that only responds based on the provided context.

        The context contains a title and a content of products on a Market Store.

        If the context is empty you MUST reply with:
        "Não consegui encontrar nenhuma informação relevante."

        If the context DOES NOT have the product the user is looking for you MUST reply with:
        "Infelizmente não temos este produto."

        Always answer in Portuguese, even if the question is in English.

        Context:
        \'{context}\'
        """
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{user_prompt}"),
            ]
        )

    def _load_vector_store(self) -> Optional[FAISS]:
        """Carrega a base de vetores existente."""
        try:
            return FAISS.load_local(
                self.vector_store_path,
                self.embedding_model,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            st.error(f"Erro ao carregar a base de vetores: {e}")
            return None

    def add_documents_to_vector_store(self, file_path: str) -> bool:
        """Adiciona documentos ao vetor de armazenamento a partir de um arquivo CSV."""
        try:
            df = pd.read_csv(file_path)
            documents = []

            # Barra de progresso do Streamlit
            progress_bar = st.progress(0)
            status_text = st.empty()

            total_rows = len(df)
            for index, row in df.iterrows():
                text = f"Title: {row['title']} | Content: {row['content']}"
                # Converte todos os valores para string para evitar problemas com tipos de dados
                metadata = {col: str(row[col]) for col in df.columns}
                documents.append(Document(page_content=text, metadata=metadata))

                # Atualiza barra de progresso
                progress = (index + 1) / total_rows
                progress_bar.progress(progress)
                status_text.text(f"Processando documento {index + 1}/{total_rows}")

            status_text.text(
                f"Criando índice de vetores para {len(documents)} documentos..."
            )

            # Cria ou atualiza o vetor de armazenamento
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(
                    documents, self.embedding_model
                )
            else:
                self.vector_store.add_documents(documents)

            self.vector_store.save_local(self.vector_store_path)
            status_text.text(f"Base de vetores salva em {self.vector_store_path}")
            time.sleep(1)  # Permite que o usuário veja a mensagem
            status_text.empty()
            progress_bar.empty()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar documentos: {e}")
            return False

    def retrieve_relevant_documents(
        self, query: str, k: int = 5
    ) -> List[Tuple[Document, float]]:
        """Recupera documentos relevantes com base na consulta do usuário."""
        if self.vector_store is None:
            st.warning(
                "Base de vetores não encontrada. Por favor, adicione documentos primeiro."
            )
            return []

        query_embedding = self.embedding_model.embed_query(query)
        return self.vector_store.similarity_search_with_score_by_vector(
            query_embedding, k=k
        )

    def answer_query(
        self, user_prompt: str, k: int = 5, threshold: float = SIMILARITY_THRESHOLD
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Processa a consulta do usuário e gera uma resposta com base nos documentos recuperados."""
        if self.vector_store is None:
            return (
                "Base de vetores não encontrada. Por favor, adicione documentos primeiro.",
                [],
            )

        # Recupera documentos relevantes
        retrieved_docs_and_scores = self.retrieve_relevant_documents(user_prompt, k)

        if not retrieved_docs_and_scores:
            return (
                "Não consegui responder à sua pergunta. Por favor, tente novamente.",
                [],
            )

        docs_content = []
        docs_info = []

        for doc, score in retrieved_docs_and_scores:
            similarity = round(
                (1 - score) * 100, 2
            )  # Converte distância para percentual

            doc_info = {
                "content": doc.page_content,
                "similarity": similarity,
                "metadata": doc.metadata,
            }
            docs_info.append(doc_info)

            if similarity > threshold:
                docs_content.append(doc.page_content)

        if not docs_content:
            return "Não temos informações sobre esse produto.", docs_info

        # Prepara o contexto e gera a resposta
        docs_content_str = "\n".join(docs_content)
        chain = self.prompt_template | self.llm | StrOutputParser()

        try:
            with st.spinner("Gerando resposta..."):
                response = chain.invoke(
                    {"context": docs_content_str, "user_prompt": user_prompt}
                )
            return response, docs_info
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")
            return (
                "Ocorreu um erro ao processar sua consulta. Por favor, tente novamente.",
                docs_info,
            )


# Interface Streamlit
st.set_page_config(
    page_title="Assistente de Produtos - RAG",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicialização da sessão
if "assistant" not in st.session_state:
    st.session_state.assistant = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar para configurações
with st.sidebar:
    st.title("⚙️ Configurações")

    # Seleção de modelo
    st.subheader("Modelos")

    llm_model = st.selectbox(
        "Modelo LLM",
        [
            "hermes-3-llama-3.2-3b",
            "llama3.2-3b-perguntas",
        ],
        index=0,
    )

    embedding_model = st.selectbox("Modelo de Embedding", ["nomic-embed-text"], index=0)

    # Parâmetros de geração
    st.subheader("Parâmetros")

    temperature = st.slider(
        "Temperatura",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Valores mais altos geram respostas mais criativas, valores mais baixos geram respostas mais determinísticas.",
    )

    similarity_threshold = st.slider(
        "Limiar de Similaridade (%)",
        min_value=0,
        max_value=100,
        value=25,
        step=5,
        help="Percentual mínimo de similaridade para incluir um documento no contexto.",
    )

    top_k = st.slider(
        "Número de Documentos (k)",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        help="Número de documentos a serem recuperados para cada consulta.",
    )

    # Configurações de dados
    st.subheader("Dados")

    vector_store_path = st.text_input(
        "Caminho da Base de Vetores", value=VECTOR_STORE_PATH
    )

    data_file = st.text_input("Arquivo de Dados CSV", value=DATA_FILE)

    # Botão para inicializar/reinicializar o assistente
    if st.button("Inicializar Assistente"):
        with st.spinner("Inicializando assistente..."):
            st.session_state.assistant = ProductAssistant(
                llm_model=llm_model,
                embedding_model_name=embedding_model,
                vector_store_path=vector_store_path,
                temperature=temperature,
            )
            st.success("Assistente inicializado com sucesso!")

    # Botão para adicionar documentos
    if st.button("Processar Dados CSV"):
        if st.session_state.assistant is None:
            st.warning("Por favor, inicialize o assistente primeiro.")
        elif os.path.exists(data_file):
            with st.spinner(f"Processando arquivo {data_file}..."):
                success = st.session_state.assistant.add_documents_to_vector_store(
                    data_file
                )
                if success:
                    st.success(f"Dados do arquivo {data_file} processados com sucesso!")
                else:
                    st.error("Falha ao processar os dados.")
        else:
            st.error(f"Arquivo {data_file} não encontrado!")

    # Botão para limpar o histórico
    if st.button("Limpar Histórico"):
        st.session_state.chat_history = []
        st.success("Histórico limpo com sucesso!")

# Área principal
st.title("🛒 Assistente de Produtos - RAG")
st.markdown("""
Este assistente usa a tecnologia RAG (Retrieval-Augmented Generation) para responder perguntas sobre produtos.
Faça uma pergunta sobre um produto para receber informações relevantes!
O modelo fiap-tc3-model foi fine tunado a fim de responder perguntas sobre produtos de forma com que o usuario seja mais propenso a compra-los.
""")

# Verificar se o assistente está inicializado
if st.session_state.assistant is None:
    st.info("Por favor, inicialize o assistente no painel lateral antes de começar.")

# Área de chat
st.subheader("💬 Chat")

# Exibir histórico de chat
for i, (query, response, docs) in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        st.write(response)

        # Botão para expandir/colapsar detalhes
        if st.button("Mostrar documentos recuperados", key=f"show_docs_{i}"):
            st.markdown("#### Documentos Recuperados")
            for j, doc in enumerate(docs):
                with st.expander(
                    f"🔹 Documento {j + 1} - Similaridade: {doc['similarity']}%"
                ):
                    st.markdown(f"**Conteúdo:** {doc['content']}")
                    st.markdown("**Metadados:**")
                    st.json(doc["metadata"])

# Campo de entrada do usuário
user_query = st.chat_input("Digite sua pergunta sobre produtos...")

# Processar a consulta do usuário
if user_query:
    if st.session_state.assistant is None:
        st.error(
            "Assistente não inicializado. Por favor, inicialize o assistente no painel lateral."
        )
    else:
        # Exibir a mensagem do usuário
        with st.chat_message("user"):
            st.write(user_query)

        # Gerar e exibir a resposta
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response, docs_info = st.session_state.assistant.answer_query(
                user_query, k=top_k, threshold=similarity_threshold
            )
            response_placeholder.write(response)

            # Adicionar à história
            st.session_state.chat_history.append((user_query, response, docs_info))

            # Mostrar os documentos recuperados
            if docs_info:
                with st.expander("Ver documentos recuperados"):
                    for i, doc in enumerate(docs_info):
                        st.markdown(f"##### Documento {i + 1}")
                        st.markdown(f"**Similaridade:** {doc['similarity']}%")
                        st.markdown(f"**Conteúdo:** {doc['content']}")
                        st.markdown("**Metadados**")
                        st.json(doc["metadata"])
            else:
                st.info("Nenhum documento relevante foi encontrado.")
