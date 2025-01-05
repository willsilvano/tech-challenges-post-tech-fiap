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
      - projetos (lista de dicionários, cada um com etapas)
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
        },
        {
            "nome": "Projeto Epsilon",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Levantamento de Requisitos",
                    "duracao_dias": 12,
                    "habilidades_necessarias": ["analysis"],
                    "cargo_necessario": "analista"
                },
                {
                    "id": 2,
                    "nome": "Planejamento",
                    "duracao_dias": 7,
                    "habilidades_necessarias": ["python", "sql"],
                    "cargo_necessario": "desenvolvedor backend"
                },
                {
                    "id": 3,
                    "nome": "Validação",
                    "duracao_dias": 5,
                    "habilidades_necessarias": ["qa"],
                    "cargo_necessario": "QA"
                }
            ]
        },
        {
            "nome": "Projeto Zeta",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Arquitetura",
                    "duracao_dias": 10,
                    "habilidades_necessarias": ["sql", "postgresql"],
                    "cargo_necessario": "DBA"
                },
                {
                    "id": 2,
                    "nome": "Implementação",
                    "duracao_dias": 20,
                    "habilidades_necessarias": ["python", "analysis"],
                    "cargo_necessario": "desenvolvedor backend"
                }
            ]
        },
        {
            "nome": "Projeto Theta",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Definição de Escopo",
                    "duracao_dias": 5,
                    "habilidades_necessarias": ["analysis"],
                    "cargo_necessario": "analista"
                },
                {
                    "id": 2,
                    "nome": "Codificação",
                    "duracao_dias": 15,
                    "habilidades_necessarias": ["python"],
                    "cargo_necessario": "desenvolvedor backend"
                },
                {
                    "id": 3,
                    "nome": "Testes",
                    "duracao_dias": 7,
                    "habilidades_necessarias": ["qa"],
                    "cargo_necessario": "QA"
                }
            ]
        },
        {
            "nome": "Projeto Iota",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Configuração de Ambiente",
                    "duracao_dias": 3,
                    "habilidades_necessarias": ["postgresql", "sql"],
                    "cargo_necessario": "DBA"
                },
                {
                    "id": 2,
                    "nome": "Integração",
                    "duracao_dias": 12,
                    "habilidades_necessarias": ["python", "sql"],
                    "cargo_necessario": "desenvolvedor backend"
                },
                {
                    "id": 3,
                    "nome": "Implantação",
                    "duracao_dias": 8,
                    "habilidades_necessarias": ["qa"],
                    "cargo_necessario": "QA"
                }
            ]
        },
        {
            "nome": "Projeto Kappa",
            "etapas": [
                {
                    "id": 1,
                    "nome": "Análise Preliminar",
                    "duracao_dias": 10,
                    "habilidades_necessarias": ["analysis"],
                    "cargo_necessario": "analista"
                },
                {
                    "id": 2,
                    "nome": "Desenvolvimento Back-End",
                    "duracao_dias": 20,
                    "habilidades_necessarias": ["python"],
                    "cargo_necessario": "desenvolvedor backend"
                }
            ]
        }
    ]

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

# def avaliar(individuo, tarefas_globais, colaboradores):
#     alocacoes = {c["id"]: [] for c in colaboradores}
#     penalidade = 0
#     makespan = 0
#
#     inicio_projeto = {t["projeto"]: 0 for t in tarefas_globais}
#     fim_projeto = {t["projeto"]: 0 for t in tarefas_globais}
#
#     # print(fim_projeto)
#
#     # Criar mapeamento de tarefas por projeto para checagem de sequência
#     tarefas_por_projeto = {}
#     for t in tarefas_globais:
#         if t["projeto"] not in tarefas_por_projeto:
#             tarefas_por_projeto[t["projeto"]] = []
#         tarefas_por_projeto[t["projeto"]].append(t)
#
#     for projeto, tarefas in tarefas_por_projeto.items():
#         tarefas_por_projeto[projeto] = sorted(tarefas, key=lambda x: x["task_id"])
#
#     # Iterar sobre as tarefas no cromossomo
#     for i, t in enumerate(tarefas_globais):
#         cid = individuo[i]
#         colab = next(x for x in colaboradores if x["id"] == cid)
#
#         # Habilidade e cargo
#         if not t["habilidades_necessarias"].issubset(colab["habilidades"]):
#             penalidade += 10_000
#         if t["cargo_necessario"] != colab["cargo"]:
#             penalidade += 10_000
#
#         # Calcula o início da tarefa
#         # print(fim_projeto[t["projeto"]])
#         inicio_tarefa = max(fim_projeto[t["projeto"]], max([a[1] for a in alocacoes[cid]] or [0]))
#         fim_tarefa = inicio_tarefa + t["duracao_dias"]
#
#         # Verifica ausências
#         for d in range(inicio_tarefa, fim_tarefa):
#             if d in colab["ausencias"]:
#                 penalidade += 500
#                 break
#
#         # print(tarefas_por_projeto)
#         # raise Exception("stop")
#
#         # Penalizar se a ordem das tarefas do projeto não estiver correta
#         posicao_tarefa = tarefas_por_projeto[t["projeto"]].index(t)
#         if posicao_tarefa > 0:
#             # print(fim_projeto[t["projeto"]])
#             tarefa_anterior = tarefas_por_projeto[t["projeto"]][posicao_tarefa - 1]
#             if fim_projeto[t["projeto"]] < fim_projeto.get(tarefa_anterior["task_id"], 0):
#                 # print(posicao_tarefa)
#                 penalidade += 5_000
#
#         # Atualiza intervalos
#         alocacoes[cid].append((inicio_tarefa, fim_tarefa))
#         fim_projeto[t["projeto"]] = fim_tarefa
#
#         if fim_tarefa > makespan:
#             makespan = fim_tarefa
#
#     # Sobreposições
#     for cid, intervals in alocacoes.items():
#         for i1 in range(len(intervals)):
#             for i2 in range(i1+1, len(intervals)):
#                 s1, e1 = intervals[i1]
#                 s2, e2 = intervals[i2]
#                 if not (e1 <= s2 or e2 <= s1):
#                     penalidade += 2000
#
#     return makespan + penalidade

def avaliar(individuo, tarefas_globais, colaboradores):
    """
    Avalia um indivíduo da população considerando:
    - Habilidades e cargo dos colaboradores.
    - Ausências dos colaboradores.
    - Ordem correta das etapas dos projetos.
    - Conflitos de sobreposição para o mesmo colaborador.
    - Conflitos de sobreposição de atividades do mesmo projeto.
    """
    alocacoes = {c["id"]: [] for c in colaboradores}
    penalidade = 0
    makespan = 0

    # Controle de término por projeto
    fim_projeto = {t["projeto"]: 0 for t in tarefas_globais}

    # Mapeamento de tarefas por projeto para validar sequência
    tarefas_por_projeto = {}
    for t in tarefas_globais:
        if t["projeto"] not in tarefas_por_projeto:
            tarefas_por_projeto[t["projeto"]] = []
        tarefas_por_projeto[t["projeto"]].append(t)

    # Ordenar tarefas de cada projeto por `task_id`
    for projeto in tarefas_por_projeto:
        tarefas_por_projeto[projeto] = sorted(tarefas_por_projeto[projeto], key=lambda x: x["task_id"])

    # Intervalos por projeto para verificar sobreposições
    intervalos_projetos = {projeto: [] for projeto in tarefas_por_projeto}

    # Avaliação das tarefas no cromossomo
    for i, t in enumerate(tarefas_globais):
        cid = individuo[i]
        colab = next(x for x in colaboradores if x["id"] == cid)

        # Verificar habilidades e cargo
        if not t["habilidades_necessarias"].issubset(colab["habilidades"]):
            penalidade += 10_000
        if t["cargo_necessario"] != colab["cargo"]:
            penalidade += 10_000

        # Calcular início e fim da tarefa baseado na sequência do projeto
        posicao_tarefa = tarefas_por_projeto[t["projeto"]].index(t)
        if posicao_tarefa > 0:
            tarefa_anterior = tarefas_por_projeto[t["projeto"]][posicao_tarefa - 1]
            inicio_tarefa = max(fim_projeto[t["projeto"]], fim_projeto[tarefa_anterior["projeto"]])
        else:
            inicio_tarefa = fim_projeto[t["projeto"]]
        fim_tarefa = inicio_tarefa + t["duracao_dias"]

        # Verificar ausências do colaborador
        for d in range(inicio_tarefa, fim_tarefa):
            if d in colab["ausencias"]:
                penalidade += 500
                break

        # Atualizar intervalos de alocação e término do projeto
        alocacoes[cid].append((inicio_tarefa, fim_tarefa))
        intervalos_projetos[t["projeto"]].append((inicio_tarefa, fim_tarefa))
        fim_projeto[t["projeto"]] = fim_tarefa

        # Atualizar makespan
        makespan = max(makespan, fim_tarefa)

    # Verificar sobreposições para o mesmo colaborador
    for cid, intervals in alocacoes.items():
        for i1 in range(len(intervals)):
            for i2 in range(i1 + 1, len(intervals)):
                s1, e1 = intervals[i1]
                s2, e2 = intervals[i2]
                if not (e1 <= s2 or e2 <= s1):  # Conflito de sobreposição
                    penalidade += 2000

    # Verificar sobreposições de atividades do mesmo projeto
    for projeto, intervals in intervalos_projetos.items():
        for i1 in range(len(intervals)):
            for i2 in range(i1 + 1, len(intervals)):
                s1, e1 = intervals[i1]
                s2, e2 = intervals[i2]
                if not (e1 <= s2 or e2 <= s1):  # Conflito de sobreposição
                    penalidade += 5000

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
    "Projeto Alpha": "#FF5733",  # Vermelho-alaranjado
    "Projeto Beta": "#33FF55",  # Verde
    "Projeto Gama": "#3355FF",  # Azul
    "Projeto Delta": "#FF33F7",  # Rosa
    "Projeto Epsilon": "#FFD700",  # Dourado
    "Projeto Zeta": "#FF00FF",  # Laranja-avermelhado
    "Projeto Theta": "#7B68EE",  # Roxo
    "Projeto Iota": "#20B2AA",  # Azul-esverdeado
    "Projeto Kappa": "#808080",  # Cinza
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

    if st.sidebar.button("Executar Algoritmo"):
        # Gera dados
        colaboradores, projetos = gerar_dados()
        tarefas_globais, colaboradores = montar_tarefas_globais(colaboradores, projetos)

        best_ind, best_val, hist_fit = algoritmo_genetico(
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

        st.session_state["df_result"] = df_res
        st.session_state["melhor_fit"] = best_val
        st.session_state["hist_fit"] = hist_fit

    tab_result, tab_calendar = st.tabs(["Resultados do Algoritmo", "Calendário & Filtros"])

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

        if "melhor_fit" in  st.session_state:
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

    # with tab_calendar:
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
                        "color": PROJECT_COLORS.get(row["Projeto"], "#999999"),
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


if __name__ == "__main__":
    main()
