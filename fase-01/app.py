import pickle

import pandas as pd
import streamlit as st
import os


def transform_categorical_to_numeric(df):
    new_df = df.copy()

    new_df['sex'] = 1 if df['sex'].iloc[0] == 'male' else 0
    new_df['smoker'] = 1 if df['smoker'].iloc[0] == 'yes' else 0

    new_df['region_northeast'] = 1 if df['region'].iloc[0] == 'northeast' else 0
    new_df['region_northwest'] = 1 if df['region'].iloc[0] == 'northwest' else 0
    new_df['region_southeast'] = 1 if df['region'].iloc[0] == 'southeast' else 0
    new_df['region_southwest'] = 1 if df['region'].iloc[0] == 'southwest' else 0

    new_df.drop('region', axis=1, inplace=True)

    return new_df


def calculate(age, sex, bmi, children, smoker, region):
    sex = 'male' if sex == 'Masculino' else 'female'
    smoker = 'yes' if smoker == 'Sim' else 'no'

    if region == 'Nordeste':
        region = 'northeast'
    elif region == 'Noroeste':
        region = 'northwest'
    elif region == 'Sudeste':
        region = 'southeast'
    elif region == 'Sudoeste':
        region = 'southwest'

    data = {
        'age': [age],
        'sex': [sex],
        'bmi': [bmi],
        'children': [children],
        'smoker': [smoker],
        'region': [region]
    }
    print(data)

    df = pd.DataFrame(data)
    df2 = transform_categorical_to_numeric(df)

    pickel_file = os.path.join('dados/pipeline_model.pkl')
    with open(pickel_file, 'rb') as file:
        model = pickle.load(file)

    charges = model.predict(df2)

    return charges


st.title('Tech Challenge - Pós Tech FIAP')
st.write("### Predicão do Custo Médico do Plano de Saúde")

st.write("Preencha os detalhes abaixo para estimar o custo do seguro:")

col1, col2, col3, col4, col5, col6 = st.columns([5, 8, 5, 5, 5, 8])

with col1:
    age = st.number_input('Idade', step=1, min_value=18, max_value=100)

with col2:
    sex = st.selectbox(
        'Sexo',
        ('Masculino', 'Feminino')
    )

with col3:
    bmi = st.number_input('IMC', step=0.1, min_value=0.0, max_value=100.0)

with col4:
    children = st.number_input('Nº Filhos', step=1, min_value=0, max_value=20)

with col5:
    smoker = st.selectbox(
        'Fumante',
        ('Sim', 'Não')
    )

with col6:
    region = st.selectbox(
        'Região',
        ('Sudoeste', 'Sudeste', 'Noroeste', 'Nordeste')
    )

calculate_result = calculate(age, sex, bmi, children, smoker, region)

st.subheader(f'Custo Estimado: ${calculate_result[0]:.2f}')
