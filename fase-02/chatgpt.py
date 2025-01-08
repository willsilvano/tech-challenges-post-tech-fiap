import datetime
import json
import random

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


##############################################################################
# 1. FUNÇÕES DE DATA
##############################################################################

def date_to_int(date_str, ref_date):
    """
    Converte uma string 'YYYY-MM-DD' em um inteiro (dias) desde ref_date.
    """
    ano, mes, dia = map(int, date_str.split("-"))
    d = datetime.date(ano, mes, dia)
    delta = d - ref_date
    return delta.days


def int_to_date(days, ref_date):
    """
    Converte um inteiro (dias desde ref_date) em 'YYYY-MM-DD'.
    """
    target_date = ref_date + datetime.timedelta(days=days)
    return target_date.strftime("%Y-%m-%d")


def read_json_from_file(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


##############################################################################
# 2. GERAÇÃO DE DADOS (MAIS COLABORADORES E PROJETOS)
##############################################################################

def gerar_dados():
    """
    Gera e retorna:
      - colaboradores (lista de dicionários)
      - projetos (lista de dicionários, cada um com etapas)
    """
    colaboradores = read_json_from_file("colaboradores.json")

    projetos = read_json_from_file("projetos.json")

    return colaboradores, projetos


def montar_tarefas_globais(colaboradores, projetos):
    tarefas_globais = []
    for proj in projetos:
        # Ordena as etapas do projeto por id
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


##############################################################################
# 3. FUNÇÕES DO GA
##############################################################################

def criar_individuo(num_tarefas, lista_colab_ids):
    return [random.choice(lista_colab_ids) for _ in range(num_tarefas)]


def populacao_inicial(tam_pop, num_tarefas, lista_colab_ids):
    return [criar_individuo(num_tarefas, lista_colab_ids) for _ in range(tam_pop)]


def avaliar(
        individuo,
        tarefas_globais,
        colaboradores,
        peso_makespan=500
):
    """
    Avalia o cromossomo (indivíduo) e retorna (fitness, penalidades).
    - As tarefas do mesmo projeto são forçadas em sequência.
    - Tarefas de projetos diferentes podem rodar em paralelo
      se houver colaborador(es) livres.
    """

    # Alocações de cada colaborador
    alocacoes = {col["id"]: [] for col in colaboradores}

    # Fim do projeto (garantir sequência dentro de cada projeto)
    fim_projeto = {}
    for t in tarefas_globais:
        if t["projeto"] not in fim_projeto:
            fim_projeto[t["projeto"]] = 0

    # Intervalos de cada projeto (para checar sobreposição, se for proibido)
    intervalos_projetos = {}
    for t in tarefas_globais:
        intervalos_projetos.setdefault(t["projeto"], [])

    penalidades = {
        "habilidades_incorretas": 0,
        "cargo_incorreto": 0,
        "ausencias": 0,
        "sobreposicoes_colaborador": 0,
        "sobreposicoes_projeto": 0
    }

    makespan = 0

    for i, tarefa in enumerate(tarefas_globais):
        cid = individuo[i]
        colab = next(c for c in colaboradores if c["id"] == cid)

        # Se colaborador não possui todas as habilidades
        if not tarefa["habilidades_necessarias"].issubset(colab["habilidades"]):
            penalidades["habilidades_incorretas"] += 10_000

        # Se cargo não confere
        if tarefa["cargo_necessario"] != colab["cargo"]:
            penalidades["cargo_incorreto"] += 10_000

        # Início da tarefa:
        #   - Respeitar o fim do projeto (sequência) para este projeto
        #   - Respeitar o fim do mesmo colaborador (sem sobreposição de si mesmo)
        proj_atual = tarefa["projeto"]
        ultimo_fim_proj = fim_projeto[proj_atual]

        if len(alocacoes[cid]) > 0:
            ultimo_fim_colab = max(e for (s, e) in alocacoes[cid])
        else:
            ultimo_fim_colab = 0

        inicio_tarefa = max(ultimo_fim_proj, ultimo_fim_colab)
        fim_tarefa = inicio_tarefa + tarefa["duracao_dias"]

        # Ausências
        # (aqui poderia ser set de dias inteiros, mas você tem como strings.
        #  então revise se está usando 'int' ou datas.
        #  no exemplo, iremos supor que 'colab["ausencias"]' possa ser um set de ints)
        for dia in range(inicio_tarefa, fim_tarefa):
            if dia in colab["ausencias"]:
                penalidades["ausencias"] += 500
                break

        # Atualizar fim do projeto
        fim_projeto[proj_atual] = fim_tarefa

        # Registrar no colaborador
        alocacoes[cid].append((inicio_tarefa, fim_tarefa))

        # Registrar no projeto
        intervalos_projetos[proj_atual].append((inicio_tarefa, fim_tarefa))

        # Atualizar makespan
        if fim_tarefa > makespan:
            makespan = fim_tarefa

    # Verificar sobreposições de um mesmo colaborador
    for cid, intervals in alocacoes.items():
        intervals_sorted = sorted(intervals, key=lambda x: x[0])
        for i1 in range(len(intervals_sorted)):
            for i2 in range(i1 + 1, len(intervals_sorted)):
                s1, e1 = intervals_sorted[i1]
                s2, e2 = intervals_sorted[i2]
                # Se (s1 < e2) e (s2 < e1), overlap
                if (s1 < e2) and (s2 < e1):
                    penalidades["sobreposicoes_colaborador"] += 2000

    # Verificar sobreposições dentro do mesmo projeto (se quiser proibir)
    # mas aqui, se voce REALMENTE quer 100% sequência,
    # isso já é garantido com 'fim_projeto', então não necessariamente precisa.
    for pid, intervals in intervalos_projetos.items():
        intervals_sorted = sorted(intervals, key=lambda x: x[0])
        for i1 in range(len(intervals_sorted)):
            for i2 in range(i1 + 1, len(intervals_sorted)):
                s1, e1 = intervals_sorted[i1]
                s2, e2 = intervals_sorted[i2]
                if (s1 < e2) and (s2 < e1):
                    # Se for 100% proibido rodar duas etapas do mesmo projeto ao mesmo tempo:
                    penalidades["sobreposicoes_projeto"] += 5000

    # Adicionar penalidade do makespan ao dicionário
    penalidades["makespan"] = makespan * peso_makespan

    soma_pens = sum(penalidades.values())
    fitness = soma_pens + penalidades["makespan"]
    return fitness, penalidades


def torneio(populacao, fitnesses, k=3):
    indices = random.sample(range(len(populacao)), k)
    best_idx = indices[0]
    best_fit = fitnesses[best_idx]
    for idx in indices[1:]:
        if fitnesses[idx] < best_fit:
            best_fit = fitnesses[idx]
            best_idx = idx
    return best_idx


def crossover(ind1, ind2):
    size = len(ind1)
    if size < 2:
        return ind1[:], ind2[:]
    cx = random.randint(1, size - 1)
    f1 = ind1[:cx] + ind2[cx:]
    f2 = ind2[:cx] + ind1[cx:]
    return f1, f2


def mutacao(individuo, lista_colab_ids, taxa_mut=0.1):
    for i in range(len(individuo)):
        if random.random() < taxa_mut:
            individuo[i] = random.choice(lista_colab_ids)
    return individuo


def algoritmo_genetico(tam_pop, n_gen, pc, pm, tarefas_globais, colaboradores):
    """
    Retorna:
      best_sol (lista de IDs)
      best_fit (float com o fitness)
      historico_fitness (lista com o melhor fitness a cada geração)
      detalhes_penalidades (dict com penalidades acumuladas do melhor indivíduo)
    """
    num_t = len(tarefas_globais)
    colab_ids = [c["id"] for c in colaboradores]
    pop = populacao_inicial(tam_pop, num_t, colab_ids)

    # Avaliação inicial
    fits_and_penalties = [avaliar(ind, tarefas_globais, colaboradores) for ind in pop]
    fits = [fit for fit, _ in fits_and_penalties]
    penalties = [penalty for _, penalty in fits_and_penalties]

    best_sol = None
    best_fit = float("inf")
    best_penalty = {}
    historico_fitness = []

    for gen in range(n_gen):
        new_pop = []
        new_fits = []
        new_penalties = []

        # Elitismo simples
        for i, f in enumerate(fits):
            if f < best_fit:
                best_fit = f
                best_sol = pop[i][:]
                best_penalty = penalties[i]

        # Salva o melhor fitness da geração atual
        historico_fitness.append(best_fit)

        while len(new_pop) < tam_pop:
            p1 = pop[torneio(pop, fits)]
            p2 = pop[torneio(pop, fits)]

            if random.random() < pc:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1[:], p2[:]

            if random.random() < pm:
                c1 = mutacao(c1, colab_ids, 0.1)
            if random.random() < pm:
                c2 = mutacao(c2, colab_ids, 0.1)

            new_pop.append(c1)
            if len(new_pop) < tam_pop:
                new_pop.append(c2)

        # Avaliação da nova população
        fits_and_penalties = [avaliar(ind, tarefas_globais, colaboradores) for ind in new_pop]
        new_fits = [fit for fit, _ in fits_and_penalties]
        new_penalties = [penalty for _, penalty in fits_and_penalties]

        pop = new_pop
        fits = new_fits
        penalties = new_penalties

    # Última checagem após todas as gerações
    for i, f in enumerate(fits):
        if f < best_fit:
            best_fit = f
            best_sol = pop[i][:]
            best_penalty = penalties[i]

    # Adiciona fitness final ao histórico
    historico_fitness.append(best_fit)

    return best_sol, best_fit, historico_fitness, best_penalty


##############################################################################
# 4. FULLCALENDAR
##############################################################################


def gerar_fullcalendar_html(eventos, initial_date):
    import json
    ev_str = json.dumps(eventos)

    css_dark = """
    body {
      color: #FFF !important;
      background-color: #1E1E1E;
    }
    .fc-daygrid-day-frame,
    .fc-event-title,
    .fc-daygrid-event-dot {
      color: #FFF !important;
    }
    .fc .fc-scrollgrid {
      border-color: #666 !important;
    }
    .fc .fc-daygrid-day-bg {
      background-color: #2A2A2A;
    }
    .fc-tooltip {
      position: absolute;
      z-index: 9999;
      background: rgba(0,0,0,0.9);
      color: #fff;
      padding: 5px 10px;
      border-radius: 3px;
      font-size: 0.85em;
      pointer-events: none;
      transition: opacity 0.1s ease;
    }
    """

    html_code = f"""
    <html>
    <head>
      <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/index.global.min.css' rel='stylesheet' />
      <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/index.global.min.js'></script>
      <style>{css_dark}</style>
    </head>
    <body>
      <div id='calendar'></div>
      <script>
        var toolTipEl;
        document.addEventListener('DOMContentLoaded', function() {{
          var calendarEl = document.getElementById('calendar');
          var calendar = new FullCalendar.Calendar(calendarEl, {{
            initialView: 'dayGridMonth',
            initialDate: '{initial_date}',
            locale: 'pt-br',
            events: {ev_str},
            eventMouseEnter: function(info) {{
              var props = info.event.extendedProps;
              var ttHtml = ''
                + '<b>Projeto:</b> ' + props.projeto + '<br>'
                + '<b>Tarefa:</b> ' + props.tarefa + '<br>'
                + '<b>Colab:</b> ' + props.colaborador + '<br>'
                + '<b>Início:</b> ' + props.dataInicio + '<br>'
                + '<b>Término:</b> ' + props.dataFim + '<br>'
                + '<b>Duração:</b> ' + props.duracao + ' dias';
              toolTipEl = document.createElement('div');
              toolTipEl.className = 'fc-tooltip';
              toolTipEl.innerHTML = ttHtml;
              document.body.appendChild(toolTipEl);
              var rect = info.el.getBoundingClientRect();
              toolTipEl.style.top = rect.top + window.scrollY + 'px';
              toolTipEl.style.left = rect.left + 'px';
            }},
            eventMouseLeave: function(info) {{
              if(toolTipEl) {{
                document.body.removeChild(toolTipEl);
                toolTipEl = null;
              }}
            }},
            editable: false
          }});
          calendar.render();
        }});
      </script>
    </body>
    </html>
    """
    return html_code


##############################################################################
# 5. STREAMLIT APP
##############################################################################

def verificar_conflitos(df_result):
    """
    Recebe o DF final (com colab, início e fim em dias) e identifica:
    1. Conflitos de intervalos para o mesmo colaborador.
    2. Conflitos de etapas do mesmo projeto sendo executadas ao mesmo tempo.

    Retorna um DataFrame 'df_conflitos' com os detalhes dos conflitos e o motivo.
    """
    # Copiar e organizar os dados
    df = df_result.copy()
    df["start_dt"] = df["Início (dias)"]
    df["end_dt"] = df["Fim (dias)"]

    conflitos = []

    # Verificar conflitos para o mesmo colaborador
    for colab, group in df.groupby("Colaborador"):
        rows = group.sort_values("start_dt").to_dict("records")
        for i1 in range(len(rows)):
            for i2 in range(i1 + 1, len(rows)):
                r1 = rows[i1]
                r2 = rows[i2]
                s1, e1 = r1["start_dt"], r1["end_dt"]
                s2, e2 = r2["start_dt"], r2["end_dt"]

                # Overlap se (s1 < e2) e (s2 < e1)
                if (s1 < e2) and (s2 < e1):
                    conflitos.append({
                        "Tipo": "Colaborador",
                        "Colaborador": colab,
                        "Projeto": f'{r1["Projeto"]} / {r2["Projeto"]}',
                        "Tarefa 1": r1["Nome Tarefa"],
                        "Período 1": f"{r1['start_dt']} - {r1['end_dt']}",
                        "Tarefa 2": r2["Nome Tarefa"],
                        "Período 2": f"{r2['start_dt']} - {r2['end_dt']}",
                        "Motivo": "Conflito de tarefas atribuídas ao mesmo colaborador",
                    })

    # Verificar conflitos entre etapas do mesmo projeto
    for projeto, group in df.groupby("Projeto"):
        rows = group.sort_values("start_dt").to_dict("records")
        for i1 in range(len(rows)):
            for i2 in range(i1 + 1, len(rows)):
                r1 = rows[i1]
                r2 = rows[i2]
                s1, e1 = r1["start_dt"], r1["end_dt"]
                s2, e2 = r2["start_dt"], r2["end_dt"]

                # Overlap se (s1 < e2) e (s2 < e1)
                if (s1 < e2) and (s2 < e1):
                    conflitos.append({
                        "Tipo": "Projeto",
                        "Colaborador": f'{r1["Colaborador"]} / {r2["Colaborador"]}',
                        "Projeto": projeto,
                        "Tarefa 1": r1["Nome Tarefa"],
                        "Período 1": f"{r1['start_dt']} - {r1['end_dt']}",
                        "Tarefa 2": r2["Nome Tarefa"],
                        "Período 2": f"{r2['start_dt']} - {r2['end_dt']}",
                        "Motivo": "Conflito de etapas sobrepostas no mesmo projeto",
                    })

    # Retorna os conflitos como DataFrame
    df_conflitos = pd.DataFrame(conflitos)
    return df_conflitos


def gerar_tabela_html(df, duracao_maxima):
    """
    Gera uma tabela HTML completa com uma coluna Gantt.

    Parâmetros:
    - df: DataFrame com os dados.
    - duracao_maxima: Duração total máxima para normalizar as barras.

    Retorno:
    - Uma string contendo o HTML completo da tabela.
    """
    # Cabeçalho da tabela
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
                <th>Início (dias)</th>
                <th>Fim (dias)</th>
                <th>Colaborador</th>
                <th>Dias</th>
                <th style="width: 150px;">Gantt</th>
            </tr>
        </thead>
        <tbody>
    """

    # Adicionar as linhas da tabela
    for _, row in df.iterrows():
        # Calcular a posição e largura da barra Gantt
        proporcao_inicio = (row["Início (dias)"] / duracao_maxima) * 100
        proporcao_duracao = ((row["Fim (dias)"] - row["Início (dias)"]) / duracao_maxima) * 100

        gantt_html = f"""
        <div class="gantt">
            <div class="gantt-bar" style="left: {proporcao_inicio}%; width: {proporcao_duracao}%;"></div>
        </div>
        """

        tabela_html += f"""
        <tr>
            <td>{row['Projeto']}</td>
            <td>{row['Nome Tarefa']}</td>
            <td>{row['Início (dias)']}</td>
            <td>{row['Fim (dias)']}</td>
            <td>{row['Colaborador']}</td>
            <td>{row['Duração (dias)']}</td>
            <td>{gantt_html}</td>
        </tr>
        """

    # Fechar a tabela
    tabela_html += """
        </tbody>
    </table>
    """
    return tabela_html


def main():
    st.title("Algoritmo Genético para Alocação de Colaboradores")

    if "df_result" not in st.session_state:
        st.session_state["df_result"] = None
        st.session_state["melhor_fit"] = None
        st.session_state["hist_fit"] = None  # evolução da fitness

    st.sidebar.header("Parâmetros do AG")
    tam_pop = st.sidebar.slider("Tamanho da População", 10, 50, 20)
    n_gen = st.sidebar.slider("Número de Gerações", 5, 1000, 20)
    pc = st.sidebar.slider("Prob. Crossover", 0.0, 1.0, 0.7)
    pm = st.sidebar.slider("Prob. Mutação", 0.0, 1.0, 0.3)

    colaboradores, projetos = gerar_dados()

    if st.sidebar.button("Executar Algoritmo"):
        tarefas_globais, colaboradores = montar_tarefas_globais(colaboradores, projetos)

        project_colors = {proj["nome"]: proj["color"] for proj in projetos}

        best_ind, best_val, hist_fit, detalhes_penalidades = algoritmo_genetico(
            tam_pop, n_gen, pc, pm, tarefas_globais, colaboradores
        )

        # Montar df_result
        project_end = {}  # armazena o último "dia" em que cada projeto terminou

        rows = []
        for i, tsk in enumerate(tarefas_globais):
            cid = best_ind[i]
            colab = next(c for c in colaboradores if c["id"] == cid)
            duracao = tsk["duracao_dias"]

            # Pega o último dia ocupado pelo mesmo colaborador:
            fim_colab = max([r["Fim (dias)"] for r in rows if r["Colaborador"] == colab["nome"]] or [0])

            # Pega o último dia ocupado pelo mesmo projeto:
            fim_proj = project_end.get(tsk["projeto"], 0)

            # Agora sim, o início deve ser depois que o colaborador está livre
            # E também depois que a etapa anterior do mesmo projeto acabou:
            start = max(fim_colab, fim_proj)

            end = start + duracao

            # Atualiza o dicionário de controle do projeto
            project_end[tsk["projeto"]] = end

            rows.append({
                "Projeto": tsk["projeto"],
                "Nome Tarefa": tsk["nome"],
                "Início (dias)": start,
                "Fim (dias)": end,
                "Colaborador": colab["nome"],
                "Duração (dias)": duracao,
            })

        df_res = pd.DataFrame(rows)

        # Adicionar a tabela Gantt como HTML
        duracao_maxima = df_res["Fim (dias)"].max()
        tabela_html = gerar_tabela_html(df_res, duracao_maxima)

        st.session_state["df_result"] = df_res
        st.session_state["table_result"] = tabela_html
        st.session_state["melhor_fit"] = best_val
        st.session_state["hist_fit"] = hist_fit
        st.session_state["detalhes_penalidades"] = detalhes_penalidades

    tab_result, tab_calendar, tab_gantt = st.tabs(["Resultados do Algoritmo", "Calendário & Filtros", "Gantt"])

    with tab_result:
        if st.session_state["df_result"] is None:
            st.info("Rode o Algoritmo na barra lateral.")
        else:
            st.subheader("Resultados Gerais")
            st.write(f"**Melhor Fitness**: {st.session_state['melhor_fit']}")
            st.table(st.session_state["df_result"])

        if st.session_state["hist_fit"]:
            st.subheader("Evolução da Fitness")
            df_fit = pd.DataFrame({
                "Geração": range(1, len(st.session_state["hist_fit"]) + 1),
                "Fitness": st.session_state["hist_fit"]
            })
            st.line_chart(df_fit, x="Geração", y="Fitness")

        if "melhor_fit" in st.session_state:
            st.write('Melhor Fitness: ')
            st.write(st.session_state["melhor_fit"])

        # Verificar conflitos
        if "df_result" in st.session_state and st.session_state["df_result"] is not None:
            st.subheader("Conflitos de Alocação")
            df_conf = verificar_conflitos(st.session_state["df_result"])
            if df_conf.empty:
                st.success("Nenhum conflito encontrado! :)")
            else:
                st.warning("Há conflitos de alocação! Veja abaixo:")
                st.table(df_conf)

    with tab_calendar:
        df_result = st.session_state["df_result"]
        if df_result is None:
            st.info("Rode o Algoritmo.")
        else:
            st.subheader("Filtros")
            projetos_unicos = sorted(df_result["Projeto"].unique())
            colabs_unicos = sorted(df_result["Colaborador"].unique())

            filtro_proj = st.multiselect("Projeto", projetos_unicos, default=projetos_unicos)
            filtro_colab = st.multiselect("Colaborador", colabs_unicos, default=colabs_unicos)

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

                    eventos.append({
                        "title": f"{row['Nome Tarefa']} - {row['Colaborador']}",
                        "start": (datetime.date.today() + datetime.timedelta(days=ini_dias)).strftime("%Y-%m-%d"),
                        "end": (datetime.date.today() + datetime.timedelta(days=fim_dias)).strftime("%Y-%m-%d"),
                        "color": project_colors.get(row["Projeto"], "#999999"),
                        "extendedProps": {
                            "projeto": row["Projeto"],
                            "tarefa": row["Nome Tarefa"],
                            "colaborador": row["Colaborador"],
                            "duracao": row["Duração (dias)"],
                            "inicioDias": ini_dias,
                            "fimDias": fim_dias,
                        }
                    })

                cal_html = gerar_fullcalendar_html(eventos, datetime.date.today().strftime("%Y-%m-%d"))
                components.html(cal_html, height=700, scrolling=True)

        st.subheader("Detalhamento das Penalidades")

        if "detalhes_penalidades" in st.session_state:

            for motivo, valor in st.session_state["detalhes_penalidades"].items():
                st.write(f"**{motivo.replace('_', ' ').capitalize()}:** {valor}")
    with tab_gantt:
        components.html(st.session_state["table_result"], height=2600, scrolling=True)


if __name__ == "__main__":
    main()
