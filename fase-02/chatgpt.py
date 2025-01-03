import streamlit as st
import streamlit.components.v1 as components
import random
import datetime
import pandas as pd

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


##############################################################################
# 2. GERAÇÃO DE DADOS (MAIS COLABORADORES E PROJETOS)
##############################################################################

def gerar_dados():
    """
    Gera e retorna:
      - colaboradores (lista de dicionários)
      - projetos (lista de dicionários, cada um com data_inicio e etapas)
    """
    colaboradores = [
        {
            "id": 101,
            "nome": "Willian",
            "habilidades": ["python", "sql"],
            "cargo": "desenvolvedor backend",
            "ausencias": ["2024-01-05", "2024-02-01"]
        },
        {
            "id": 102,
            "nome": "Marco",
            "habilidades": ["analysis", "qa", "audit"],
            "cargo": "QA",
            "ausencias": ["2024-01-15", "2024-01-16"]
        },
        {
            "id": 103,
            "nome": "Rafaela",
            "habilidades": ["analysis", "python"],
            "cargo": "analista",
            "ausencias": []
        },
        {
            "id": 104,
            "nome": "Luiz",
            "habilidades": ["postgresql", "sql"],
            "cargo": "DBA",
            "ausencias": ["2024-01-10", "2024-01-11"]
        },
        {
            "id": 105,
            "nome": "Juliana",
            "habilidades": ["qa", "audit", "analysis"],
            "cargo": "QA",
            "ausencias": ["2024-01-20"]
        },
        {
            "id": 106,
            "nome": "Paulo",
            "habilidades": ["python", "sql", "analysis"],
            "cargo": "desenvolvedor backend",
            "ausencias": ["2024-01-25", "2024-01-26"]
        },
        {
            "id": 107,
            "nome": "Fernanda",
            "habilidades": ["analysis", "python", "audit"],
            "cargo": "analista",
            "ausencias": ["2024-02-02"]
        },
        {
            "id": 108,
            "nome": "Carla",
            "habilidades": ["qa", "audit"],
            "cargo": "QA",
            "ausencias": ["2024-01-29", "2024-02-05"]
        },
        {
            "id": 109,
            "nome": "Sérgio",
            "habilidades": ["postgresql", "sql"],
            "cargo": "DBA",
            "ausencias": []
        },
    ]

    projetos = [
        {
            "nome": "Projeto Alpha",
            "data_inicio": "2024-01-01",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Análise",
                    "duracao_dias": 10,
                    "habilidades_necessarias": ["analysis"],
                    "cargo_necessario": "analista"
                },
                {
                    "id": 2,
                    "nome": "Desenvolvimento",
                    "duracao_dias": 15,
                    "habilidades_necessarias": ["python"],
                    "cargo_necessario": "desenvolvedor backend"
                },
                {
                    "id": 3,
                    "nome": "Revisão SQL",
                    "duracao_dias": 5,
                    "habilidades_necessarias": ["sql"],
                    "cargo_necessario": "desenvolvedor backend"
                },
            ]
        },
        {
            "nome": "Projeto Beta",
            "data_inicio": "2024-01-05",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Análise Beta",
                    "duracao_dias": 5,
                    "habilidades_necessarias": ["analysis"],
                    "cargo_necessario": "analista"
                },
                {
                    "id": 2,
                    "nome": "QA Beta",
                    "duracao_dias": 10,
                    "habilidades_necessarias": ["qa"],
                    "cargo_necessario": "QA"
                },
                {
                    "id": 3,
                    "nome": "Ajustes no Banco",
                    "duracao_dias": 8,
                    "habilidades_necessarias": ["sql", "postgresql"],
                    "cargo_necessario": "DBA"
                }
            ]
        },
        {
            "nome": "Projeto Gama",
            "data_inicio": "2024-02-01",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Modelagem Gama",
                    "duracao_dias": 7,
                    "habilidades_necessarias": ["sql"],
                    "cargo_necessario": "DBA"
                },
                {
                    "id": 2,
                    "nome": "Auditoria Gama",
                    "duracao_dias": 5,
                    "habilidades_necessarias": ["audit"],
                    "cargo_necessario": "QA"
                }
            ]
        },
        {
            "nome": "Projeto Delta",
            "data_inicio": "2024-02-10",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Análise Delta",
                    "duracao_dias": 8,
                    "habilidades_necessarias": ["analysis"],
                    "cargo_necessario": "analista"
                },
                {
                    "id": 2,
                    "nome": "Dev Delta",
                    "duracao_dias": 10,
                    "habilidades_necessarias": ["python"],
                    "cargo_necessario": "desenvolvedor backend"
                }
            ]
        }
    ]

    return colaboradores, projetos

def montar_tarefas_globais(colaboradores, projetos):
    """
    1) Descobre a menor data_inicio entre os projetos -> data_referencia
    2) Converte ausencias de cada colaborador p/ dias (int) desde data_referencia
    3) Gera lista global de tarefas
    """
    datas_inicios = [datetime.datetime.strptime(p["data_inicio"], "%Y-%m-%d").date()
                     for p in projetos]
    data_referencia = min(datas_inicios)

    # Converter ausencias
    for c in colaboradores:
        c["ausencias"] = {date_to_int(d, data_referencia) for d in c["ausencias"]}

    # Montar tarefas
    tarefas_globais = []
    for proj in projetos:
        proj_nome = proj["nome"]
        offset_inicio = date_to_int(proj["data_inicio"], data_referencia)
        acumulador = offset_inicio

        for etapa in proj["etapas"]:
            start_day = acumulador
            end_day = acumulador + etapa["duracao_dias"]
            tarefas_globais.append({
                "projeto": proj_nome,
                "task_id": etapa["id"],
                "nome": etapa["nome"],
                "start": start_day,
                "end": end_day,
                "habilidades_necessarias": set(etapa["habilidades_necessarias"]),
                "cargo_necessario": etapa["cargo_necessario"],
            })
            acumulador = end_day

    return tarefas_globais, colaboradores, data_referencia

##############################################################################
# 3. FUNÇÕES DO GA
##############################################################################

def criar_individuo(num_tarefas, lista_colab_ids):
    return [random.choice(lista_colab_ids) for _ in range(num_tarefas)]

def populacao_inicial(tam_pop, num_tarefas, lista_colab_ids):
    return [criar_individuo(num_tarefas, lista_colab_ids) for _ in range(tam_pop)]

def avaliar(individuo, tarefas_globais, colaboradores):
    alocacoes = {c["id"]: [] for c in colaboradores}
    penalidade = 0
    makespan = 0

    for i, t in enumerate(tarefas_globais):
        cid = individuo[i]
        colab = next(x for x in colaboradores if x["id"] == cid)

        # Habilidade e cargo
        if not t["habilidades_necessarias"].issubset(colab["habilidades"]):
            penalidade += 10_000
        if t["cargo_necessario"] != colab["cargo"]:
            penalidade += 10_000

        # Ausencias
        for d in range(t["start"], t["end"]):
            if d in colab["ausencias"]:
                penalidade += 500
                break

        # Guarda intervalos
        alocacoes[cid].append((t["start"], t["end"]))

        if t["end"] > makespan:
            makespan = t["end"]

    # Sobreposições
    for cid, intervals in alocacoes.items():
        for i1 in range(len(intervals)):
            for i2 in range(i1+1, len(intervals)):
                s1, e1 = intervals[i1]
                s2, e2 = intervals[i2]
                if not (e1 <= s2 or e2 <= s1):
                    penalidade += 2000

    return makespan + penalidade

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
    """
    num_t = len(tarefas_globais)
    colab_ids = [c["id"] for c in colaboradores]
    pop = populacao_inicial(tam_pop, num_t, colab_ids)
    fits = [avaliar(ind, tarefas_globais, colaboradores) for ind in pop]

    best_sol = None
    best_fit = float("inf")
    historico_fitness = []

    for gen in range(n_gen):
        new_pop = []
        new_fits = []

        # elitismo simples
        for i, f in enumerate(fits):
            if f < best_fit:
                best_fit = f
                best_sol = pop[i][:]

        # Salva o melhor da geração atual
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

        pop = new_pop
        fits = [avaliar(ind, tarefas_globais, colaboradores) for ind in pop]

    # ultima checagem
    for i, f in enumerate(fits):
        if f < best_fit:
            best_fit = f
            best_sol = pop[i][:]

    # Adiciona fitness final
    historico_fitness.append(best_fit)

    return best_sol, best_fit, historico_fitness

##############################################################################
# 4. FULLCALENDAR
##############################################################################

PROJECT_COLORS = {
    "Projeto Alpha": "#FF5733",
    "Projeto Beta": "#33FF55",
    "Projeto Gama": "#3355FF",
    "Projeto Delta": "#FF33F7",
}

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
    Recebe o DF final (com colab, Data Início, Data Fim) e identifica
    se há algum colaborador com intervalos sobrepostos.

    Retorna um DataFrame 'df_conflitos' com colab, tarefa1, tarefa2, datas, etc.
    Se não houver conflitos, retorna DF vazio.
    """

    # Precisamos converter Data Início / Fim pra datetime e comparar intervalos.
    df = df_result.copy()
    df["start_dt"] = pd.to_datetime(df["Data Início"])
    df["end_dt"] = pd.to_datetime(df["Data Fim"]) + pd.Timedelta(days=1)  # excludente

    conflitos = []
    # agrupar por colaborador
    for colab, group in df.groupby("Colaborador"):
        rows = group.sort_values("start_dt").to_dict("records")
        # comparar cada par
        for i1 in range(len(rows)):
            for i2 in range(i1+1, len(rows)):
                r1 = rows[i1]
                r2 = rows[i2]
                s1, e1 = r1["start_dt"], r1["end_dt"]
                s2, e2 = r2["start_dt"], r2["end_dt"]
                # overlap se (s1 < e2) e (s2 < e1)
                if (s1 < e2) and (s2 < e1):
                    conflitos.append({
                        "Colaborador": colab,
                        "Tarefa 1": r1["Nome Tarefa"],
                        "Período 1": f"{r1['Data Início']} - {r1['Data Fim']}",
                        "Tarefa 2": r2["Nome Tarefa"],
                        "Período 2": f"{r2['Data Início']} - {r2['Data Fim']}",
                    })

    df_conflitos = pd.DataFrame(conflitos)
    return df_conflitos


def main():
    st.title("Algoritmo Genético para Alocação de Colaboradores")

    if "df_result" not in st.session_state:
        st.session_state["df_result"] = None
        st.session_state["melhor_fit"] = None
        st.session_state["data_referencia"] = None
        st.session_state["hist_fit"] = None  # evolução da fitness

    st.sidebar.header("Parâmetros do AG")
    tam_pop = st.sidebar.slider("Tamanho da População", 10, 50, 20)
    n_gen = st.sidebar.slider("Número de Gerações", 5, 100, 20)
    pc = st.sidebar.slider("Prob. Crossover", 0.0, 1.0, 0.7)
    pm = st.sidebar.slider("Prob. Mutação", 0.0, 1.0, 0.3)

    if st.sidebar.button("Executar Algoritmo"):
        # Gera dados
        colaboradores, projetos = gerar_dados()
        tarefas_globais, colaboradores, data_referencia = montar_tarefas_globais(colaboradores, projetos)

        best_ind, best_val, hist_fit = algoritmo_genetico(
            tam_pop, n_gen, pc, pm, tarefas_globais, colaboradores
        )

        # Montar df_result
        rows = []
        for i, tsk in enumerate(tarefas_globais):
            cid = best_ind[i]
            colab = next(c for c in colaboradores if c["id"] == cid)
            s = tsk["start"]
            e = tsk["end"]
            rows.append({
                "Projeto": tsk["projeto"],
                "Nome Tarefa": tsk["nome"],
                "Data Início": int_to_date(s, data_referencia),
                "Data Fim": int_to_date(e - 1, data_referencia),
                "Colaborador": colab["nome"],
                "Duração (dias)": e - s,
            })

        df_res = pd.DataFrame(rows)

        st.session_state["df_result"] = df_res
        st.session_state["melhor_fit"] = best_val
        st.session_state["data_referencia"] = data_referencia
        st.session_state["hist_fit"] = hist_fit

    tab_result, tab_calendar = st.tabs(["Resultados do Algoritmo", "Calendário & Filtros"])

    with tab_result:
        if st.session_state["df_result"] is None:
            st.info("Rode o Algoritmo na barra lateral.")
        else:
            st.subheader("Resultados Gerais")
            st.write(f"**Melhor Fitness**: {st.session_state['melhor_fit']}")
            st.table(st.session_state["df_result"])

            # Evolução da Fitness em gráfico de linhas
            st.subheader("Evolução da Fitness ao longo das Gerações (Gráfico de Linhas)")
            hist_fit = st.session_state["hist_fit"]
            df_fit = pd.DataFrame({
                "geracao": range(1, len(hist_fit)+1),
                "fitness": hist_fit
            })

            st.line_chart(df_fit, x="geracao", y="fitness")

            # Verificar conflitos
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
            data_referencia = st.session_state["data_referencia"]

            st.subheader("Filtros")
            projetos_unicos = sorted(df_result["Projeto"].unique())
            colabs_unicos = sorted(df_result["Colaborador"].unique())

            filtro_proj = st.multiselect("Projeto", projetos_unicos, default=projetos_unicos)
            filtro_colab = st.multiselect("Colaborador", colabs_unicos, default=colabs_unicos)

            df_result["Data Início (dt)"] = pd.to_datetime(df_result["Data Início"])
            df_result["Data Fim (dt)"] = pd.to_datetime(df_result["Data Fim"])

            start_min = df_result["Data Início (dt)"].min()
            end_max = df_result["Data Fim (dt)"].max()

            start_filter = st.date_input("Data Inicial", value=start_min)
            end_filter = st.date_input("Data Final", value=end_max)

            if start_filter > end_filter:
                st.warning("Data Inicial maior que Data Final.")
                return

            df_filt = df_result[
                (df_result["Projeto"].isin(filtro_proj)) &
                (df_result["Colaborador"].isin(filtro_colab))
            ]
            df_filt = df_filt[
                (df_filt["Data Fim (dt)"] >= pd.to_datetime(start_filter)) &
                (df_filt["Data Início (dt)"] <= pd.to_datetime(end_filter))
            ]

            st.subheader("Calendário de Alocação (Filtrado)")
            if df_filt.empty:
                st.info("Nenhuma tarefa no período/filtros selecionados.")
            else:
                eventos = []
                initial_date_str = str(start_filter)

                for _, row in df_filt.iterrows():
                    ini_str = row["Data Início"]
                    fim_str = row["Data Fim"]
                    fim_excl = (pd.to_datetime(fim_str) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

                    proj = row["Projeto"]
                    colab = row["Colaborador"]
                    dur = row["Duração (dias)"]

                    eventos.append({
                        "title": f"{row['Nome Tarefa']} - {colab}",
                        "start": ini_str,
                        "end": fim_excl,
                        "color": PROJECT_COLORS.get(proj, "#999999"),
                        "extendedProps": {
                            "projeto": proj,
                            "tarefa": row["Nome Tarefa"],
                            "colaborador": colab,
                            "duracao": dur,
                            "dataInicio": ini_str,
                            "dataFim": fim_str
                        }
                    })

                cal_html = gerar_fullcalendar_html(eventos, initial_date_str)
                components.html(cal_html, height=700, scrolling=True)


if __name__ == "__main__":
    main()
