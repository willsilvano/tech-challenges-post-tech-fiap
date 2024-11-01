import pickle

import pandas as pd
import streamlit as st


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
    data = {
        'age': [age],
        'sex': [sex],
        'bmi': [bmi],
        'children': [children],
        'smoker': [smoker],
        'region': [region]
    }
    df = pd.DataFrame(data)
    df2 = transform_categorical_to_numeric(df)

    with open('fase-01/dados/pipeline_model.pkl', 'rb') as file:
        model = pickle.load(file)

    charges = model.predict(df2)

    return charges


st.title('Tech Challenge Post Tech Fiap')
st.write("### Insurance Charges Prediction")

st.write("Enter the following data:")

col1, col2, col3, col4, col5, col6 = st.columns([5, 8, 5, 5, 5, 8])

with col1:
    age = st.number_input('Age', step=1, min_value=18, max_value=100)

with col2:
    sex = st.selectbox(
        'Sex',
        ('male', 'female')
    )

with col3:
    bmi = st.number_input('BMI', step=0.1, min_value=0.0, max_value=100.0)

with col4:
    children = st.number_input('Children', step=1, min_value=0, max_value=20)

with col5:
    smoker = st.selectbox(
        'Smoker',
        ('yes', 'no')
    )

with col6:
    region = st.selectbox(
        'Region',
        ('southwest', 'southeast', 'northwest', 'northeast')
    )

calculate_result = calculate(age, sex, bmi, children, smoker, region)

st.subheader(f'The charges value are: ${calculate_result[0]:.2f}')
