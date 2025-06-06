# TECH CHALLENGE - Fase 04

Esta é uma atividade referente ao desafio final da fase 04.

## Especificações

Detalhamento do desafio.

### Prazo de Entrega

Quarta-feira, 21 de Maio de 2025, às 23h59

### O problema

O Tech Challenge desta fase será a criação de uma aplicação que utilize análise de vídeo. O seu projeto deve incorporar as técnicas de reconhecimento facial, análise de expressões emocionais em vídeos e detecção de atividades.

### A proposta do desafio

Você deverá criar uma aplicação a partir do vídeo que se encontra disponível na plataforma do aluno, e que execute as seguintes tarefas:
1. Reconhecimento facial: Identifique e marque os rostos presentes no vídeo.
2. Análise de expressões emocionais: Analise as expressões emocionais dos rostos identificados.
3. Detecção de atividades: Detecte e categorize as atividades sendo realizadas no vídeo.
4. Geração de resumo: Crie um resumo automático das principais atividades e emoções detectadas no vídeo.

### Entregável

1. Código Fonte: todo o código fonte da aplicação deve ser entregue em um repositório Git, incluindo um arquivo README com instruções claras de como executar o projeto.
2. Relatório: o resumo obtido automaticamente com as principais atividades e emoções detectadas no vídeo. Nesse momento esperando que o relatório inclua:
    - Total de frames analisados.
    - Número de anomalias detectadas.
    - Observação: movimento anômalo não segue o padrão geral de atividades (como gestos bruscos ou comportamentos atípicos) esses são classificados como anômalos.
3. Demonstração em Vídeo: um vídeo demonstrando a aplicação em funcionamento, evidenciando cada uma das funcionalidades implementadas.

### Como rodar o projeto

A seguir estão as instruções para configurar e executar o projeto em sua máquina local.

### Pré-requisitos

- Python 3.12 ou superior
- UV

### Configuração

1. Clone o repositório:

   ```bash
   git clone https://github.com/willsilvano/tech-challenges-post-tech-fiap.git
   cd tech-challenges-post-tech-fiap.git
   ```

2. Instale o UV, que é um gerenciador de dependências para Python. Para instalar, consulte a documentação oficial [aqui](https://docs.astral.sh/uv/).

3. Instale as dependências do projeto:

   ```bash
   uv sync
   ```

4. Ative o ambiente virtual:

   ```bash
   source .venv/bin/activate
   ```

### Execução da aplicação

Para executar a aplicação Streamlit e visualizar a aplicação desenvolvida em ação, utilize o seguinte comando:

```bash
cd fase-04
streamlit run app.py
```

Uma vez que o servidor estiver em execução, abra seu navegador e navegue até a URL fornecida (geralmente `http://localhost:8501`).

Você verá a interface do Streamlit com o aplicativo em execução.

### Resultado

O resultado deste tech challenge é apresentado no [vídeo de entrega](https://www.youtube.com/watch?v=KtJbryvKuUM&ab_channel=JosielEliseuBorges).