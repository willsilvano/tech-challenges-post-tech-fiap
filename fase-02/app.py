import datetime
import json
import random

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(
    page_title="Algoritmo Genético para alocação de colaboradores",
    layout="wide",
    initial_sidebar_state="expanded",
)


class Utils:
    """
    Classe utilitária para conversão de datas.
    """

    @staticmethod
    def date_to_int(date_str: str, ref_date: datetime.date) -> int:
        """
        Converte uma string de data (YYYY-MM-DD) para um inteiro que representa
        a distância (em dias) em relação a uma data de referência.

        :param date_str: Data no formato 'YYYY-MM-DD'.
        :param ref_date: Data de referência para o cálculo.
        :return: Número de dias entre a data especificada e a data de referência.
        """
        ano, mes, dia = map(int, date_str.split("-"))
        d = datetime.date(ano, mes, dia)
        delta = d - ref_date
        return delta.days

    @staticmethod
    def int_to_date(days: int, ref_date: datetime.date) -> str:
        """
        Converte um inteiro (dias) em string de data (YYYY-MM-DD),
        adicionando 'days' dias à data de referência.

        :param days: Número de dias a adicionar.
        :param ref_date: Data de referência.
        :return: Data no formato 'YYYY-MM-DD' resultante.
        """
        target_date = ref_date + datetime.timedelta(days=days)
        return target_date.strftime("%d/%m/%Y")


class DataManager:
    """
    Classe responsável por ler dados de arquivos JSON e organizar
    as informações de colaboradores e projetos.
    """

    @staticmethod
    def read_json_from_file(file_path: str) -> dict:
        """
        Lê um arquivo JSON e retorna seu conteúdo como dicionário ou lista.

        :param file_path: Caminho do arquivo JSON.
        :return: Dados carregados do arquivo JSON.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    def gerar_dados(self):
        """
        Lê as informações de colaboradores e projetos de arquivos JSON.

        :return: Tupla (colaboradores, projetos).
        """
        colaboradores = self.read_json_from_file("dados/colaboradores.json")
        projetos = self.read_json_from_file("dados/projetos.json")

        # Converte as datas de ausência de cada colaborador para dias (inteiros)
        for colab in colaboradores:
            ausencias_convertidas = []
            for data_str in colab["ausencias"]:
                dia_int = Utils.date_to_int(data_str, st.session_state.ref_date)
                ausencias_convertidas.append(dia_int)
            colab["ausencias"] = ausencias_convertidas

        return colaboradores, projetos

    def montar_tarefas_globais(self, colaboradores: list, projetos: list):
        """
        Monta uma lista global de tarefas, organizando as etapas de cada projeto.

        :param colaboradores: Lista de colaboradores.
        :param projetos: Lista de projetos, cada um contendo etapas.
        :return: Tupla (tarefas_globais, colaboradores).
        """
        tarefas_globais = []
        for proj in projetos:
            etapas_ordenadas = sorted(proj["etapas"], key=lambda e: e["id"])
            for etapa in etapas_ordenadas:
                tarefas_globais.append({
                    "projeto": proj["nome"],
                    "task_id": etapa["id"],
                    "nome": etapa["nome"],
                    "duracao_dias": etapa["duracao_dias"],
                    "habilidades_necessarias": set(etapa["habilidades_necessarias"]),
                    "cargo_necessario": etapa["cargo_necessario"],
                })
        return tarefas_globais, colaboradores


class GeneticAlgorithm:
    """
    Classe responsável por implementar o Algoritmo Genético para alocação de colaboradores.
    """

    @staticmethod
    def criar_individuo(num_tarefas: int, lista_colab_ids: list) -> list:
        """
        Cria um indivíduo (solução) selecionando aleatoriamente um colaborador para cada tarefa.

        :param num_tarefas: Quantidade de tarefas do problema.
        :param lista_colab_ids: IDs de todos os colaboradores disponíveis.
        :return: Lista de IDs de colaboradores correspondente ao indivíduo gerado.
        """
        return [random.choice(lista_colab_ids) for _ in range(num_tarefas)]

    @staticmethod
    def populacao_inicial(tam_pop: int, num_tarefas: int, lista_colab_ids: list) -> list:
        """
        Gera a população inicial para o Algoritmo Genético, criando vários indivíduos.

        :param tam_pop: Tamanho da população.
        :param num_tarefas: Quantidade total de tarefas.
        :param lista_colab_ids: IDs de todos os colaboradores disponíveis.
        :return: Lista de indivíduos (população inicial).
        """
        return [
            GeneticAlgorithm.criar_individuo(num_tarefas, lista_colab_ids)
            for _ in range(tam_pop)
        ]

    @staticmethod
    def avaliar(
            individuo: list,
            tarefas_globais: list,
            colaboradores: list,
            peso_makespan: int = 200
    ) -> tuple:
        """
        Avalia a aptidão (fitness) de um indivíduo, aplicando penalidades por incompatibilidades,
        ausências e sobreposições de tarefas, além de penalizar o makespan.

        :param individuo: Indivíduo (solução) representado por uma lista de IDs de colaboradores.
        :param tarefas_globais: Lista de tarefas globais (estrutura de cada projeto).
        :param colaboradores: Lista de colaboradores com habilidades, cargos e ausências.
        :param peso_makespan: Fator de multiplicação para o makespan no cálculo da fitness.
        :return: Tupla (fitness, penalidades), onde penalidades é um dicionário detalhado.
        """
        alocacoes = {col["id"]: [] for col in colaboradores}
        fim_projeto = {t["projeto"]: 0 for t in tarefas_globais}
        intervalos_projetos = {t["projeto"]: [] for t in tarefas_globais}

        # Dicionário que acumula os valores totais
        penalidades = {
            "habilidades_incorretas": 0,
            "cargo_incorreto": 0,
            "ausencias": 0,
            "sobreposicoes_colaborador": 0,
            "sobreposicoes_projeto": 0
        }

        # Dicionário que lista cada ocorrência das penalidades
        ocorrencias_penalidades = {
            "habilidades_incorretas": [],
            "cargo_incorreto": [],
            "ausencias": [],
            "sobreposicoes_colaborador": [],
            "sobreposicoes_projeto": [],
        }

        makespan = 0

        # Avaliação das tarefas
        for i, tarefa in enumerate(tarefas_globais):
            cid = individuo[i]
            colab = next(c for c in colaboradores if c["id"] == cid)

            # Penalidade por habilidades incorretas
            if not tarefa["habilidades_necessarias"].issubset(colab["habilidades"]):
                penalidades["habilidades_incorretas"] += 10_000
                ocorrencias_penalidades["habilidades_incorretas"].append({
                    "projeto": tarefa["projeto"],
                    "tarefa": tarefa["nome"],
                    "colaborador": colab["nome"],
                    "habilidades_necessarias": ", ".join(tarefa["habilidades_necessarias"]),
                    "habilidades_colaborador": ", ".join(colab["habilidades"])
                })

            # Penalidade por cargo incorreto
            if tarefa["cargo_necessario"] != colab["cargo"]:
                penalidades["cargo_incorreto"] += 10_000
                ocorrencias_penalidades["cargo_incorreto"].append({
                    "projeto": tarefa["projeto"],
                    "tarefa": tarefa["nome"],
                    "colaborador": colab["nome"],
                    "cargo_necessario": tarefa["cargo_necessario"],
                    "cargo_colaborador": colab["cargo"]
                })

            proj_atual = tarefa["projeto"]
            ultimo_fim_proj = fim_projeto[proj_atual]

            # Descobrir o fim da última tarefa desse colaborador
            ultimo_fim_colab = max(e for (_, e) in alocacoes[cid]) if alocacoes[cid] else 0

            inicio_tarefa = max(ultimo_fim_proj, ultimo_fim_colab)

            # Ajusta o início para não cair em ausência
            while inicio_tarefa in colab["ausencias"]:
                inicio_tarefa += 1

            fim_tarefa = inicio_tarefa
            duracao_restante = tarefa["duracao_dias"]
            while duracao_restante > 0:
                if fim_tarefa not in colab["ausencias"]:
                    duracao_restante -= 1
                fim_tarefa += 1

            # Se caiu em ausência, registrar penalidade
            for dia in range(inicio_tarefa, fim_tarefa):
                if dia in colab["ausencias"]:
                    penalidades["ausencias"] += 500
                    ocorrencias_penalidades["ausencias"].append({
                        "projeto": tarefa["projeto"],
                        "tarefa": tarefa["nome"],
                        "colaborador": colab["nome"],
                        "dia_ausencia": Utils.int_to_date(dia, st.session_state.ref_date)
                    })
                    break

            fim_projeto[proj_atual] = fim_tarefa
            alocacoes[cid].append((inicio_tarefa, fim_tarefa))
            intervalos_projetos[proj_atual].append((inicio_tarefa, fim_tarefa))

            if fim_tarefa > makespan:
                makespan = fim_tarefa

        # Penalizar sobreposições por colaborador
        for cid, intervals in alocacoes.items():
            intervals_sorted = sorted(intervals, key=lambda x: x[0])
            for i1 in range(len(intervals_sorted)):
                for i2 in range(i1 + 1, len(intervals_sorted)):
                    s1, e1 = intervals_sorted[i1]
                    s2, e2 = intervals_sorted[i2]
                    if (s1 < e2) and (s2 < e1):
                        penalidades["sobreposicoes_colaborador"] += 2000
                        ocorrencias_penalidades["sobreposicoes_colaborador"].append({
                            "colaborador": next(c["nome"] for c in colaboradores if c["id"] == cid),
                            "intervalo1": (s1, e1),
                            "intervalo2": (s2, e2)
                        })

        # Penalizar sobreposições dentro do mesmo projeto
        for pid, intervals in intervalos_projetos.items():
            intervals_sorted = sorted(intervals, key=lambda x: x[0])
            for i1 in range(len(intervals_sorted)):
                for i2 in range(i1 + 1, len(intervals_sorted)):
                    s1, e1 = intervals_sorted[i1]
                    s2, e2 = intervals_sorted[i2]
                    if (s1 < e2) and (s2 < e1):
                        penalidades["sobreposicoes_projeto"] += 5000
                        ocorrencias_penalidades["sobreposicoes_projeto"].append({
                            "projeto": proj_atual,
                            "intervalo1": (s1, e1),
                            "intervalo2": (s2, e2)
                        })

        penalidades["makespan"] = makespan * peso_makespan
        soma_pens = sum(penalidades.values())
        fitness = soma_pens  # soma de todas as penalidades (incluindo makespan)

        # Retorna também a lista de ocorrências detalhadas
        return fitness, penalidades, ocorrencias_penalidades

    @staticmethod
    def torneio(populacao: list, fitnesses: list, k: int = 3) -> int:
        """
        Seleciona o melhor indivíduo dentre k indivíduos escolhidos aleatoriamente (torneio).

        :param populacao: Lista de indivíduos.
        :param fitnesses: Lista de valores de fitness correspondentes a cada indivíduo.
        :param k: Tamanho do torneio.
        :return: Índice do melhor indivíduo escolhido.
        """
        indices = random.sample(range(len(populacao)), k)
        best_idx = indices[0]
        best_fit = fitnesses[best_idx]
        for idx in indices[1:]:
            if fitnesses[idx] < best_fit:
                best_fit = fitnesses[idx]
                best_idx = idx
        return best_idx

    @staticmethod
    def crossover(ind1: list, ind2: list) -> tuple:
        """
        Realiza o crossover entre dois indivíduos, trocando uma parte de seus genes.

        :param ind1: Indivíduo 1 (lista de IDs de colaboradores).
        :param ind2: Indivíduo 2 (lista de IDs de colaboradores).
        :return: Uma tupla com dois novos indivíduos resultantes do crossover.
        """
        size = len(ind1)
        if size < 2:
            return ind1[:], ind2[:]
        cx = random.randint(1, size - 1)
        f1 = ind1[:cx] + ind2[cx:]
        f2 = ind2[:cx] + ind1[cx:]
        return f1, f2

    @staticmethod
    def mutacao(individuo: list, lista_colab_ids: list, taxa_mut: float = 0.1) -> list:
        """
        Aplica mutação a um indivíduo, trocando ocasionalmente o colaborador de uma tarefa.

        :param individuo: Indivíduo (lista de IDs de colaboradores).
        :param lista_colab_ids: IDs de todos os colaboradores disponíveis.
        :param taxa_mut: Probabilidade de mutar uma determinada tarefa.
        :return: Indivíduo mutado.
        """
        for i in range(len(individuo)):
            if random.random() < taxa_mut:
                individuo[i] = random.choice(lista_colab_ids)
        return individuo

    def algoritmo_genetico(
            self,
            tam_pop: int,
            n_gen: int,
            pc: float,
            pm: float,
            tarefas_globais: list,
            colaboradores: list
    ) -> tuple:
        """
        Executa o loop principal do Algoritmo Genético, gerando e evoluindo a população
        ao longo de n_gen gerações.

        :param tam_pop: Tamanho da população.
        :param n_gen: Número de gerações.
        :param pc: Probabilidade de crossover.
        :param pm: Probabilidade de mutação.
        :param tarefas_globais: Lista de todas as tarefas (estrutura do problema).
        :param colaboradores: Lista de colaboradores com suas habilidades, cargos e ausências.
        :return: Tupla contendo (melhor_solucao, melhor_fitness, historico_fitness, melhor_penalty).
        """
        num_t = len(tarefas_globais)
        colab_ids = [c["id"] for c in colaboradores]

        # População inicial
        pop = self.populacao_inicial(tam_pop, num_t, colab_ids)

        # Avalia a população inicial
        fits_and_penalties = [
            self.avaliar(ind, tarefas_globais, colaboradores)
            for ind in pop
        ]
        fits = [item[0] for item in fits_and_penalties]
        penalties = [item[1] for item in fits_and_penalties]
        penalties_occurrences = [item[2] for item in fits_and_penalties]

        best_sol = None
        best_fit = float("inf")
        best_penalty = {}
        best_penalty_occurrences = {}

        historico_fitness = []

        # Loop principal de gerações
        for _ in range(n_gen):
            new_pop = []
            new_fits = []
            new_penalties = []
            new_occurrences = []

            # Atualiza melhor indivíduo
            for i, f in enumerate(fits):
                if f < best_fit:
                    best_fit = f
                    best_sol = pop[i][:]
                    best_penalty = penalties[i]
                    best_penalty_occurrences = penalties_occurrences[i]

            historico_fitness.append(best_fit)

            # Gerar nova população
            while len(new_pop) < tam_pop:
                p1 = pop[self.torneio(pop, fits)]
                p2 = pop[self.torneio(pop, fits)]

                if random.random() < pc:
                    c1, c2 = self.crossover(p1, p2)
                else:
                    c1, c2 = p1[:], p2[:]

                if random.random() < pm:
                    c1 = self.mutacao(c1, colab_ids, 0.1)
                if random.random() < pm:
                    c2 = self.mutacao(c2, colab_ids, 0.1)

                new_pop.append(c1)
                if len(new_pop) < tam_pop:
                    new_pop.append(c2)

            # Avalia nova população
            fits_and_penalties = [
                self.avaliar(ind, tarefas_globais, colaboradores)
                for ind in new_pop
            ]
            new_fits = [item[0] for item in fits_and_penalties]
            new_penalties = [item[1] for item in fits_and_penalties]
            new_occurrences = [item[2] for item in fits_and_penalties]

            pop = new_pop
            fits = new_fits
            penalties = new_penalties
            penalties_occurrences = new_occurrences

        # Avaliação final
        for i, f in enumerate(fits):
            if f < best_fit:
                best_fit = f
                best_sol = pop[i][:]
                best_penalty = penalties[i]
                best_penalty_occurrences = penalties_occurrences[i]

        historico_fitness.append(best_fit)

        return best_sol, best_fit, historico_fitness, best_penalty, best_penalty_occurrences


class Visualization:
    """
    Classe que agrega funções de geração de componentes de visualização,
    tais como calendário e Gantt, além de verificação de conflitos.
    """

    @staticmethod
    def gerar_fullcalendar_html(eventos: list, initial_date: str) -> str:
        """
        Gera código HTML contendo um calendário interativo (FullCalendar)
        que exibe os eventos (tarefas).

        :param eventos: Lista de eventos (tarefas) no formato aceito pelo FullCalendar.
        :param initial_date: Data inicial a ser exibida no calendário.
        :return: String HTML que renderiza o calendário.
        """
        ev_str = json.dumps(eventos)

        css_custom = """
        body {
            font-family: 'Arial', sans-serif;
            font-size: 14px;
            color: #333;
        }
        .fc {
            border: 1px solid #ddd;
            background-color: #fff;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .fc-toolbar-title {
            font-size: 18px;
            font-weight: bold;
            color: #444;
        }
        .fc-button {
            background-color: #0056b3;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 12px;
        }
        .fc-button:hover {
            background-color: #003d82;
        }
        .fc-event {
            font-size: 12px;
            border-radius: 4px;
            padding: 2px 5px;
            font-weight: bold;
        }
        .fc-daygrid-day-number {
            color: #555;
        }
        .fc-event-title {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .fc-tooltip {
            position: absolute;
            z-index: 9999;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
        """

        html_code = f"""
        <html>
        <head>
            <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/index.global.min.css' rel='stylesheet' />
            <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/index.global.min.js'></script>
            <style>{css_custom}</style>
        </head>
        <body>
            <div id='calendar'></div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var calendarEl = document.getElementById('calendar');
                    var tooltip;  // Tooltip global
                    var calendar = new FullCalendar.Calendar(calendarEl, {{
                        initialView: 'dayGridMonth',
                        initialDate: '{initial_date}',
                        locale: 'pt-br',
                        headerToolbar: {{
                            left: 'prev,next today',
                            center: 'title',
                            right: 'dayGridMonth,timeGridWeek,timeGridDay'
                        }},
                        buttonText: {{
                            today: 'Hoje',
                            month: 'Mês',
                            week: 'Semana',
                            day: 'Dia'
                        }},
                        events: {ev_str},
                        eventMouseEnter: function(info) {{
                            var props = info.event.extendedProps;
                            tooltip = document.createElement('div');
                            tooltip.className = 'fc-tooltip';
                            tooltip.style.position = 'absolute';
                            tooltip.style.background = 'rgba(0,0,0,0.8)';
                            tooltip.style.color = 'white';
                            tooltip.style.padding = '10px';
                            tooltip.style.borderRadius = '5px';
                            tooltip.style.fontSize = '12px';
                            tooltip.style.pointerEvents = 'none';
                            tooltip.innerHTML = `
                                <b>Projeto:</b> ${{props.projeto}}<br>
                                <b>Tarefa:</b> ${{props.tarefa}}<br>
                                <b>Colaborador:</b> ${{props.colaborador}}<br>
                                <b>Início:</b> ${{props.dataInicio}}<br>
                                <b>Término:</b> ${{props.dataFim}}<br>
                                <b>Duração:</b> ${{props.duracao}} dias
                            `;
                            document.body.appendChild(tooltip);
                            var rect = info.el.getBoundingClientRect();
                            tooltip.style.top = rect.top + window.scrollY + 10 + 'px';
                            tooltip.style.left = rect.left + 'px';
                        }},
                        eventMouseLeave: function(info) {{
                            if (tooltip) {{
                                tooltip.remove();  // Remove o tooltip do DOM
                                tooltip = null;
                            }}
                        }},
                        editable: false,
                        height: "auto",
                        weekends: false  // Oculta os finais de semana no calendário
                    }});
                    calendar.render();
                }});
            </script>
        </body>
        </html>
        """
        return html_code

    @staticmethod
    def gerar_tabela_html(df: pd.DataFrame, duracao_maxima: int) -> str:
        """
        Gera código HTML contendo uma tabela que ilustra um gráfico de Gantt simplificado
        para as tarefas listadas no DataFrame.

        :param df: DataFrame com as colunas necessárias para renderização (Início, Fim, etc.).
        :param duracao_maxima: Duração total (maior valor de fim).
        :return: String HTML que exibe a tabela com barras de Gantt.
        """
        tabela_html = """
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
            }
            .gantt {
                width: 100%;
                height: 15px;
                position: relative;
                background-color: #e0e0e0;
            }
            .gantt-bar {
                position: absolute;
                height: 100%;
                background-color: #1f77b4;
            }
        </style>
        <table>
            <thead>
                <tr>
                    <th style="width: 150px;">Projeto</th>
                    <th>Nome Tarefa</th>
                    <th>Data Início</th>
                    <th>Data Fim</th>
                    <th>Colaborador</th>
                    <th>Trabalho (dias)</th>
                    <th>Duração (dias)</th>
                    <th style="width: 150px;">Gantt</th>
                </tr>
            </thead>
            <tbody>
        """

        for _, row in df.iterrows():
            proporcao_inicio = (row["Início (dias)"] / duracao_maxima) * 100
            proporcao_duracao = (
                                        (row["Fim (dias)"] - row["Início (dias)"]) / duracao_maxima
                                ) * 100

            # Calculando a duração como diferença entre Data Início e Data Fim
            data_inicio = pd.to_datetime(row["Data Início"], format="%d/%m/%Y")
            data_fim = pd.to_datetime(row["Data Fim"], format="%d/%m/%Y")
            duracao_dias = (data_fim - data_inicio).days + 1  # +1 para incluir o último dia

            gantt_html = f"""
            <div class="gantt">
                <div class="gantt-bar" style="left: {proporcao_inicio}%; width: {proporcao_duracao}%;"></div>
            </div>
            """

            tabela_html += f"""
            <tr>
                <td>{row['Projeto']}</td>
                <td>{row['Nome Tarefa']}</td>
                <td>{row['Data Início']}</td>
                <td>{row['Data Fim']}</td>
                <td>{row['Colaborador']}</td>
                <td>{row['Duração (dias)']}</td>  <!-- Renomeado para Trabalho -->
                <td>{duracao_dias}</td>  <!-- Nova coluna Duração -->
                <td>{gantt_html}</td>
            </tr>
            """

        tabela_html += """
            </tbody>
        </table>
        """
        return tabela_html


class App:
    """
    Classe principal da aplicação Streamlit, responsável pela interação com o usuário,
    execução do Algoritmo Genético e exibição dos resultados.
    """

    def __init__(self):
        """
        Inicializa as classes auxiliares.
        """
        self.data_manager = DataManager()
        self.ga = GeneticAlgorithm()
        self.vis = Visualization()

    def run(self):
        """
        Executa a aplicação Streamlit, construindo a interface e
        gerenciando o fluxo de dados e visualizações.
        """
        st.title("Algoritmo Genético para alocação de colaboradores")

        # Estado inicial (variáveis de sessão)
        if "df_result" not in st.session_state:
            st.info("Execute o algoritmo na barra lateral.")
            st.session_state["table_result"] = None
            st.session_state["df_result"] = None
            st.session_state["melhor_fit"] = None
            st.session_state["hist_fit"] = None

        # Sidebar
        st.sidebar.header("Parâmetros")
        tam_pop = st.sidebar.slider("Tamanho da população", 10, 100, 20)
        n_gen = st.sidebar.slider("Número de gerações", 5, 1000, 100)
        pc = st.sidebar.slider("Prob. crossover", 0.0, 1.0, 0.7)
        pm = st.sidebar.slider("Prob. mutação", 0.0, 1.0, 0.3)
        st.sidebar.date_input("Data de referência", datetime.date(2025, 1, 1), key="ref_date")

        # Gera dados
        colaboradores, projetos = self.data_manager.gerar_dados()
        project_colors = {proj["nome"]: proj["color"] for proj in projetos}

        if st.sidebar.button("Executar"):
            # Monta tarefas globais
            tarefas_globais, colaboradores = self.data_manager.montar_tarefas_globais(
                colaboradores, projetos
            )

            # Executa Algoritmo Genético
            best_ind, best_val, hist_fit, detalhes_penalidades, ocorrencias_penalidades = self.ga.algoritmo_genetico(
                tam_pop, n_gen, pc, pm, tarefas_globais, colaboradores
            )

            # Reconstrói o cronograma final (df_res)
            project_end = {}
            rows = []
            for i, tsk in enumerate(tarefas_globais):
                cid = best_ind[i]
                colab = next(c for c in colaboradores if c["id"] == cid)
                duracao = tsk["duracao_dias"]

                fim_colab = max(
                    [r["Fim (dias)"] + 1 for r in rows if r["Colaborador"] == colab["nome"]] or [0]
                )
                fim_proj = project_end.get(tsk["projeto"], 0)

                start = max(fim_colab, fim_proj)
                while start in colab["ausencias"] or (
                        st.session_state.ref_date + datetime.timedelta(days=start)
                ).weekday() >= 5:
                    start += 1

                end = start
                duracao_restante = duracao
                while duracao_restante > 0:

                    if end not in colab["ausencias"] and (
                            st.session_state.ref_date + datetime.timedelta(days=end)
                    ).weekday() < 5:
                        duracao_restante -= 1
                    end += 1

                project_end[tsk["projeto"]] = end

                start_date = (
                        st.session_state.ref_date + datetime.timedelta(days=start)
                ).strftime("%d/%m/%Y")
                end_date = (
                        st.session_state.ref_date + datetime.timedelta(days=end - 1)  # -1 para incluir o último dia
                ).strftime("%d/%m/%Y")

                # Adicionar ao cronograma
                rows.append({
                    "Projeto": tsk["projeto"],
                    "Nome Tarefa": tsk["nome"],
                    "Início (dias)": start,
                    "Data Início": start_date,
                    "Fim (dias)": end - 1,  # -1 para refletir o último dia de trabalho
                    "Data Fim": end_date,
                    "Colaborador": colab["nome"],
                    "Duração (dias)": duracao,
                })

            df_res = pd.DataFrame(rows)
            duracao_maxima = df_res["Fim (dias)"].max()

            # Gera tabela Gantt em HTML
            tabela_html = self.vis.gerar_tabela_html(df_res, duracao_maxima)

            # Salva em sessão
            st.session_state["df_result"] = df_res
            st.session_state["table_result"] = tabela_html
            st.session_state["melhor_fit"] = best_val
            st.session_state["hist_fit"] = hist_fit
            st.session_state["detalhes_penalidades"] = detalhes_penalidades
            st.session_state["ocorrencias_penalidades"] = ocorrencias_penalidades

        df_result = st.session_state["df_result"]

        # Exibe resultados
        if df_result is not None:
            tab_data, tab_fitness, tab_conflicts, tab_gant, tab_calendar = st.tabs(
                ["Dados", "Fitness", "Conflitos", "Gant", "Calendário"]
            )

            with tab_data:
                st.subheader("Projetos")

                for proj in projetos:
                    st.markdown(f"**{proj['nome']}**")
                    # formata colunas etapas
                    df_etapas = []
                    for etapa in proj["etapas"]:
                        df_etapas.append({
                            "ID": etapa["id"],
                            "Nome": etapa["nome"],
                            "Duração (dias)": etapa["duracao_dias"],
                            "Habilidades": ", ".join(etapa["habilidades_necessarias"]),
                            "Cargo": etapa["cargo_necessario"]
                        })
                    st.table(pd.DataFrame(df_etapas))
                    st.divider()

                st.subheader("Colaboradores")
                df_colaboradores = []
                for colab in colaboradores:
                    df_colaboradores.append({
                        "ID": colab["id"],
                        "Nome": colab["nome"],
                        "Habilidades": ", ".join(colab["habilidades"]),
                        "Cargo": colab["cargo"],
                        "Ausências": ", ".join(
                            (st.session_state.ref_date + datetime.timedelta(days=d)).strftime("%d/%m/%Y")
                            for d in colab["ausencias"]
                        )
                    })
                st.table(pd.DataFrame(df_colaboradores))

            with tab_gant:
                components.html(st.session_state["table_result"], height=600, scrolling=True)

            with tab_conflicts:
                st.subheader("Resumo das Penalidades")

                translate_penalities = {
                    "habilidades_incorretas": "Habilidades Incorretas",
                    "cargo_incorreto": "Cargo Incorreto",
                    "ausencias": "Ausências",
                    "sobreposicoes_colaborador": "Sobreposições de Colaborador",
                    "sobreposicoes_projeto": "Sobreposições de Projeto",
                    "makespan": "Makespan"
                }

                if "detalhes_penalidades" in st.session_state:
                    df_penality = pd.DataFrame(st.session_state["detalhes_penalidades"].items(),
                                               columns=["Motivo", "Valor"])
                    df_penality["Motivo"] = df_penality["Motivo"].apply(
                        lambda x: translate_penalities[x]
                    )
                    st.dataframe(df_penality, hide_index=True)

                if "ocorrencias_penalidades" in st.session_state:
                    for tipo_pen, ocorrencias in st.session_state["ocorrencias_penalidades"].items():
                        if ocorrencias:
                            st.write(f"### {translate_penalities[tipo_pen]}")
                            df_oc = pd.DataFrame(ocorrencias)
                            st.table(df_oc)


            with tab_fitness:
                st.subheader("Evolução da Fitness")
                if st.session_state["hist_fit"]:
                    df_fit = pd.DataFrame({
                        "Geração": range(1, len(st.session_state["hist_fit"]) + 1),
                        "Fitness": st.session_state["hist_fit"]
                    })

                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=df_fit["Geração"],
                            y=df_fit["Fitness"],
                            mode='lines',
                            name='Fitness',
                            hovertemplate=(
                                "<b>Geração</b>: %{x}<br>"
                                "<b>Fitness</b>: %{y}<extra></extra>"
                            )
                        )
                    )
                    fig.update_layout(
                        xaxis_title="Gerações",
                        yaxis_title="Fitness",
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=12,
                            font_family="Arial"
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)

                if "melhor_fit" in st.session_state:
                    st.write(f"**Melhor Fitness**: {st.session_state['melhor_fit']}")

            with tab_calendar:
                st.subheader("Filtros")
                projetos_unicos = sorted(df_result["Projeto"].unique())
                colabs_unicos = sorted(df_result["Colaborador"].unique())

                filtro_proj = st.multiselect(
                    "Projeto", projetos_unicos, default=projetos_unicos
                )
                filtro_colab = st.multiselect(
                    "Colaborador", colabs_unicos, default=colabs_unicos
                )

                df_result_filtered = df_result[
                    (df_result["Projeto"].isin(filtro_proj)) &
                    (df_result["Colaborador"].isin(filtro_colab))
                    ]

                st.subheader("Calendário de Alocação (Filtrado)")
                if df_result_filtered.empty:
                    st.info("Nenhuma tarefa nos filtros selecionados.")
                else:
                    eventos = []
                    for _, row in df_result_filtered.iterrows():
                        ini_dias = row["Início (dias)"]
                        fim_dias = row["Fim (dias)"]

                        start_date = (
                                st.session_state.ref_date + datetime.timedelta(days=ini_dias)
                        ).strftime("%Y-%m-%d")
                        end_date = (
                                st.session_state.ref_date + datetime.timedelta(days=fim_dias + 1)
                        ).strftime("%Y-%m-%d")

                        # # Adicionar ao calendário
                        eventos.append({
                            "title": f"{row['Nome Tarefa']} - {row['Colaborador']}",
                            "start": start_date,
                            "end": end_date,
                            "color": project_colors.get(row["Projeto"], "#999999"),
                            "extendedProps": {
                                "projeto": row["Projeto"],
                                "tarefa": row["Nome Tarefa"],
                                "colaborador": row["Colaborador"],
                                "duracao": row["Duração (dias)"],
                                "dataInicio": row["Data Início"],
                                "dataFim": row["Data Fim"]
                            }
                        })

                    cal_html = self.vis.gerar_fullcalendar_html(
                        eventos, st.session_state.ref_date.strftime("%Y-%m-%d")
                    )
                    components.html(cal_html, height=1000, scrolling=True)


if __name__ == "__main__":
    app = App()
    app.run()
