# TECH CHALLENGE - Fase 02

Esta é uma atividade referente ao desafio final da fase 02.

## Especificações

Detalhamento do desafio.

### Prazo de Entrega

Terça-feira, 21 de Janeiro de 2025, às 23h59

### O problema

O desafio consiste em projetar, implementar e testar um sistema que utilize Algoritmos Genéticos para otimizar uma função ou resolver um problema complexo de otimização.

Você pode escolher problemas como otimização de rotas, alocação de recursos e design de redes neurais.

### Requisitos

**Definição do Problema**: escolha um problema real que possa ser resolvido por meio de otimização genética. Descreva o problema, os objetivos e os critérios de sucesso.

**Testes e Resultados**: realize testes para demonstrar a eficácia do algoritmo. Compare os resultados obtidos com métodos de solução convencionais.

**Documentação**: forneça uma documentação completa do projeto, incluindo descrição do problema, detalhes da implementação do algoritmo, análises de resultados e conclusões.

### Entregável

**Código-fonte do projeto**: deve incluir todos os scripts e códigos utilizados na implementação do algoritmo genético.

**Documento detalhado** descrevendo o problema, a abordagem utilizada, os resultados obtidos e as conclusões.

**Um vídeo explicativo do projeto**, demonstrando a aplicação prática do algoritmo e discutindo os resultados obtidos.

## Como rodar o projeto

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

Para executar a aplicação Streamlit e visualizar o algoritmo genético em ação, utilize o seguinte comando:

```bash
cd fase-02
streamlit run app.py
```

Uma vez que o servidor estiver em execução, abra seu navegador e navegue até a URL fornecida (geralmente `http://localhost:8501`).

Você verá a interface do Streamlit com o aplicativo em execução.

### Documentação

O documento final do projeto está em [Documento.md](docs/Documento.md).
