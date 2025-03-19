# %%
import pandas as pd
import html

# %%

# Carrega o CSV (substitua 'produtos.csv' pelo caminho do seu arquivo)
df = pd.read_json("fase-03/data/trn.json", lines=True)

# Selecione apenas as colunas 'title' e 'content'
df = df[["title", "content"]]

# Remove as linhas em que a coluna 'title' ou 'content' estiverem vazias
df = df[df["content"] != ""]
df = df[~df["content"].isnull()]
df = df[~df["title"].isnull()]

# filtra os content maiores quie 100 cara cteres
df = df[df["content"].str.len() > 100]

# Remove a tag <p> e o caractere &nbsp;
df["title"] = df["title"].apply(html.unescape)
df["content"] = df["content"].apply(html.unescape)

# Cria uma coluna combinada utilizando 'title' e 'content'
df["combined"] = df["title"].fillna("") + " " + df["content"].fillna("")

df.head()

df.to_csv("trn-processed.csv", index=False)

# %%
