# TECH CHALLENGE - Fase 03

Esta é uma atividade referente ao desafio final da fase 03.

## Especificações

Detalhamento do desafio.

### Prazo de Entrega

Terça-feira, 25 de Março de 2025, às 23h59

### O problema

No Tech Challenge desta fase, você precisa executar o fine-tuning de um foundation model (Llama, BERT, MISTRAL etc.), utilizando o dataset "The AmazonTitles-1.3MM". O modelo treinado deverá:
- Receber perguntas com um contexto obtido por meio do arquivo json “trn.json” que está contido dentro do dataset.
- A partir do prompt formado pela pergunta do usuário sobre o título do produto, o modelo deverá gerar uma resposta baseada na pergunta do usuário trazendo como resultado do aprendizado do fine-tuning os dados da sua descrição.

### Fluxo de trabalho

#### Escolha do Dataset

Descrição: o The AmazonTitles-1.3MM consiste em consultas textuais reais de usuários e títulos associados de produtos relevantes encontrados na Amazon e suas descrições, medidos por ações implícitas ou explícitas dos usuários.

#### Preparação do Dataset

Faça o download do dataset AmazonTitles-1.3MM e utilize o arquivo “trn.json”. Nele, você utilizará as colunas “title” e “content”, que contêm título e descrição respectivamente. Prepare os prompts para o fine-tuning garantindo que estejam organizados de maneira adequada para o treinamento do modeloescolhido. Limpe e pré-processe os dados conforme necessário para o modelo escolhido.

#### Chamada do Foundation Model

Importe o foundation model que será utilizado e faça um teste apresentando o resultado atual do modelo antes do treinamento (para que se obtenha uma base de análise após o fine-tuning), e então será possível avaliar a diferença do resultado gerado.

#### Execução do Fine-Tuning

Execute o fine-tuning do foundation model selecionado (por exemplo, BERT, GPT, Llama) utilizando o dataset preparado.

Documente o processo de fine-tuning, incluindo os parâmetros utilizados e qualquer ajuste específico realizado no modelo.

#### Geração de Respostas

Configure o modelo treinado para receber perguntas dos usuários.

O modelo deverá gerar uma resposta baseada na pergunta do usuário e nos dados provenientes do fine-tuning, incluindo as fontes fornecidas.

### Entregável

- Documento detalhando o processo de seleção e preparação do dataset.
- Descrição do processo de fine-tuning do modelo, com detalhes dos parâmetros e ajustes utilizados. Código-fonte do processo de fine-tuning.
- Um vídeo demonstrando o modelo treinado gerando respostas a partir de perguntas do usuário e utilizando o contexto obtido por meio treinamento com o fine-tuning.

### Resultado

O documento final do projeto está em [Relatório.md](docs/relatorio.md).
