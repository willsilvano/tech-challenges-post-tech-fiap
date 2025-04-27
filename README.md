# Sobre
Repositório para armazenar os desafios técnicos para a pós graduação em I.A para devs da FIAP

# Configurações

Nesse repositório foi utilizado o gerenciador de pacotes [Python UV](https://docs.astral.sh/uv/).

Para reproduzir o ambiente, basta instalar o `uv` e digitar `uv init`.

# Exportando para PDF

Para exportar os notebooks para PDF, siga os passos:

- Instale as biblitoecas necessárias: <https://nbconvert.readthedocs.io/en/latest/install.html#installing-tex>
- Execute o comando: `uv run --jupyter nbconvert caminho_arquivo.ipynb --to pdf --output nome_arquivo.pdf

# Desafios

AO final de cada uma das fases foi desenvolvido um desafio técnico (tech challenge) conforme seções a seguir.

## Fase 01

Os arquivos estão na pasta [fase-01](fase-01).

Neste desafio foi desenvolvido um modelo preditivo de regressão para prever o valor dos custos médicos individuais cobrados por um seguro de saúde fictício.

## Fase 02

Os arquivos estão na pasta [fase-02](fase-02).

Neste desafio foi desenvolvido um sistema utilizando Algoritmos Genéticos para otimizar a alocação de colaboradores em tarefas de projetos, considerando habilidades específicas dos membros da equipe, ausências, cargos e possíveis conflitos de agenda.

## Fase 03

Os arquivos estão na pasta [fase-03](fase-03).

Neste desafio foi realizado o fine-tuning de foundation models (Llama3.2 e Qwen2.5), utilizando o dataset "The AmazonTitles-1.3MM"

## Fase 04

Os arquivos estão na pasta [fase-04](fase-04).

Neste desafio foi desenvolvido um sistema de análise de vídeo, utilizando técnicas de reconhecimento facial, análise de expressões emocionais e detecção de atividades.