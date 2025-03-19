# 🛒 Assistente de Produtos RAG

Uma aplicação de Recuperação Aumentada por Geração (RAG) para responder consultas sobre produtos utilizando LangChain, FAISS, Ollama e Streamlit.

## 📌 Visão Geral

Este projeto implementa um assistente virtual para consultas sobre produtos utilizando a técnica RAG (Retrieval-Augmented Generation). O sistema recupera informações relevantes de uma base de dados de produtos e gera respostas naturais em português, mesmo quando as perguntas são feitas em inglês.

**O Sistema também usa um modelo llama3.2 fine tunado para responder as perguntas.**

## 🚀 Funcionalidades

- **Pesquisa Semântica**: Encontra produtos relevantes com base no significado da consulta, não apenas em palavras-chave
- **Interface Amigável**: Interface de chat intuitiva criada com Streamlit
- **Transparência**: Visualize quais documentos foram utilizados para gerar as respostas
- **Personalização**: Ajuste parâmetros como temperatura do modelo e limites de similaridade
- **Multilíngue**: Responde em português mesmo para consultas em inglês

## 🛠️ Tecnologias Utilizadas

- **LangChain**: Framework para criar aplicações baseadas em LLMs
- **FAISS**: Biblioteca para busca de similaridade eficiente em vetores de alta dimensão
- **Ollama**: Modelos de linguagem executados localmente
- **Streamlit**: Interface de usuário web interativa
- **Pandas**: Processamento de dados tabulares

## 📋 Pré-requisitos

- Python 3.8+
- Ollama instalado e configurado com os modelos necessários
- Arquivo CSV com dados de produtos no formato adequado

## ⚙️ Instalação

1. Instale as dependências:
   ```bash
   uv sync
   ```

2. Certifique-se de ter o Ollama instalado e os modelos configurados:
   ```bash
   # Instale o modelo
   Através do GGUF gerado no Google Colab, baixe-o e salve dentro da pasta de modelos do LMStudio.

   # Faça o deploy local dos modelos
   Na tela de `Developer` do LMStudio, selecione os dmodelos para realizar o deploy local.

   # Instale o modelo de embeddings
   ollama pull nomic-embed-text
   ```

## 📊 Estrutura de Dados

O arquivo CSV de entrada deve conter pelo menos as seguintes colunas:
- `title`: Título do produto
- `content`: Descrição ou detalhes do produto

Exemplo:
```csv
title,content,price,category
"Smartphone XYZ","Um smartphone avançado com câmera de 48MP e tela AMOLED.",999.99,Eletrônicos
```

## 🚀 Uso

1. Inicie a aplicação:
   ```bash
   streamlit run app.py
   ```

2. No painel lateral:
   - Selecione os modelos e parâmetros desejados
   - Clique em "Inicializar Assistente"
   - Clique em "Processar Dados CSV" para carregar seus dados

3. Na área principal, faça perguntas sobre produtos usando o campo de chat

## 🔧 Configurações Avançadas

### Modelos Suportados
- LLM: `llama3.2-3b-perguntas`, `llama3.2:3b`
- Embeddings: `nomic-embed-text`

### Ajustes de Parâmetros
- **Temperatura**: Afeta a criatividade das respostas (0.0 - 1.0)
- **Limiar de Similaridade**: Filtra documentos com base na relevância (0% - 100%)
- **Número de Documentos (k)**: Quantidade de documentos recuperados para cada consulta (1-10)

## 📁 Estrutura do Projeto

```
assistente-produtos-rag/
├── rag.py                # Aplicação Streamlit principal
├── data/                 # Diretório para arquivos de dados
│   └── data-1000.csv     # Exemplo de dados de produtos
├── vector_store/         # Diretório para armazenar índices FAISS
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação
```

## 📝 Exemplo de Consultas

- "Samsung Galaxy Note II Decal Vinyl Skin é uma boa compra?"
- "I want car decals"
- "Recommends me products for 3D printer"
- "Há algum item de automóveis na sua loja?"
- "Zoya Nail Polish .5 fl oz é uma boa compra?"