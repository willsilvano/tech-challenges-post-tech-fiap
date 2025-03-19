- Documento detalhando o processo de seleção e preparação do dataset.
- Descrição do processo de fine-tuning do modelo, com detalhes dos parâmetros e ajustes utilizados. Código-fonte do processo de fine-tuning.
- Um vídeo demonstrando o modelo treinado gerando respostas a partir de perguntas do usuário e utilizando o contexto obtido por meio treinamento com o fine-tuning.

## Escolha do Dataset

Foi utilizado o [dataset disponibilizado pela FIAP](https://drive.google.com/file/d/12zH4mL2RX8iSvH0VCNnd3QxO4DzuHWnK/view), que contém títulos e descrições de produtos da Amazon. Foi utilizado o arquivo trn.json

## Preparação do Dataset

A preparação do dataset foi feita utilizando o script `scripts/0-prepare-data.py`. O script lê o arquivo `trn.json` e extrai os títulos e descrições dos produtos.

Após carregado, o dataset filtra os dados, removendo as linhas onde a descrição ou título são vazios/nulos.

Além disso, são removidas as linhas em que o tamanho do texto da descrição é menor que 100 caracteres.

Após isso, é aplicado um tratamento de tags HTML, removendo todas as tags e mantendo apenas o texto.

Por fim, o dataset é salvo em um arquivo `data/trn-processed.csv`.

## Definição dos modelos para Fine Tuning

Decidimos em realizar dois processos de fine-tuning:

1. Um fine tuning para que o modelo retorne a descrição do produto a partir do título. Para esse caso foi utilizado como base o modelo `Qwen 2.5 7B` disponibilizado pelo repositório unsloth no Hugging Face.

2. Um fine tuning para que o modelo gere respostas a partir de perguntas do usuário, sobre um produto específico. Para esse caso foi utilizado como base o modelo `Llama 3.2 3B` disponibilizado pelo repositório unsloth no Hugging Face.


## Preparação para o Fine Tuning

Para realizar o fine tuning do modelo que descreve produtos, foi utilizado o dataset `data/data-1000.csv` gerado a partir do script `scripts/01-prepare-data-finetuning-1.py`. Esse script lê o arquivo `data/trn-processed.csv` e seleciona 1000 linhas aleatórias para serem utilizadas no fine tuning.

Para realizar o fine tuning do modelo que gera respostas a partir de perguntas, foi utilizado o dataset `data/dados-fine-tunning.jsonl` gerado a partir do script `scripts/02-prepare-data-finetuning-2.py`. Esse script lê o arquivo `data/data-1000.csv` e gera um arquivo jsonl com as perguntas e respostas geradas a partir dos títulos e descrições dos produtos. Para geração das perguntas e respostas, foi usado uma API desenvolvida pela equipe, que usa a API do Chat GPT. O Prompt utilizado para geração das perguntas e respostas foi:

TODO: colocar o prompt  correto
```
Pergunta: Qual é a descrição do produto: {título do produto}?
Resposta: {descrição do produto}
```

## Execução do Fine Tuning

O fine tuning do modelo que descreve produtos foi feito utilizando o script `scripts/04-fine-tuning-qwen2.5-7B.ipynb` sendo executado diretamente no Google Colab, utilizando VM com GPU de 16GB VRAM. O script carrega o modelo `Qwen 2.5 7B` e o dataset `data/data-1000.csv` e realiza o fine tuning do modelo.

O fine tuning do modelo que gera respostas a partir de perguntas foi feito utilizando o script `scripts/05-fine-tuning-llama3.2-3B.ipynb` sendo executado diretamente no Google Colab, utilizando VM com GPU de 16GB VRAM. O script carrega o modelo `Llama 3.2 3B` e o dataset `data/dados-fine-tunning.jsonl` e realiza o fine tuning do modelo.

Ambos os scripts exportam o modelo no formato GGUF para que possam ser executados localmente atraves de Ollama ou LMStudio.

## Resultados

Para verificar o resultado de ambos os modelos refinados, foi criado duas demonstrações, sendo:

1. O arquivo `agents.ipynb`: Esse script cria alguns agentes de IA, através da biblioteca LangGraph, no um assistente decisor recebe uma texto do usuário, e esse agente deve verificar se é uma pergunta ou título de um produto. Sendo um título, o modelo encaminha a mensagem para outro agente realizar a descrição do produto, utilizando o modelo Qwen 2.5 7B. Caso seja uma pergunta, o modelo encaminha a mensagem para outro agente realizar a resposta da pergunta, utilizando o modelo Llama 3.2 3B.

2. O arquivo `rag.py`: Esse script cria uma aplicação com Streamlit, na qual é possível inicializar uma vector store para execução de um RAG com base no arquivo `data/dados-1000.csv`. É possível ainda selecionar qual modelo irá responder, e o percentual de similaridade para considerar os dados de título e descrição dos produtos na busca. O usuário digita uma pergunta e o modelo retorna a resposta com base no contexto encontrado através do RAG.



