import json

import pandas as pd
import requests

INPUT_FILE = "data/data-1000.csv"
OUTPUT_FILE = "data/dados-fine-tunning.jsonl"


def create_jsonl_from_csv():
    # URL do serviço
    url = "https://HOST/simple-assistant/chatbot-sgn/fine-tuning-fiap"

    # Cabeçalhos da requisição
    headers = {
        "Authorization": "Bearer XXXXX",
        "Content-Type": "application/json",
    }

    df = pd.read_csv(INPUT_FILE)

    for index, row in df.iterrows():
        already_processed = False

        with open(OUTPUT_FILE, "r") as file:
            for linha in set(file.readlines()):
                if row["title"] in linha:
                    already_processed = True
                    print(f"Item {row['title']} already exists")

        if already_processed:
            continue

        data = {
            "text": f"""
                Titulo: {row["title"]}
                Descrição: {row["content"]}
            """
        }

        response = requests.post(url, json=data, headers=headers)

        print("Index:", index)
        print("Status Code:", response.status_code)

        if response.status_code == 200:
            print("Response JSON:", response.json()["content"])

            with open(OUTPUT_FILE, "a") as f:
                js = json.loads(response.json()["content"])
                js["context"] = f"Title: {row['title']}\nContent: {row['content']}"
                f.write(str(js) + "\n")


def create_no_context_responses():
    i = 0

    with open(OUTPUT_FILE, "r") as file:
        for index, row in enumerate(set(file.readlines())):
            try:
                if i < 100:
                    row = row.replace("'", '"')
                    js = json.loads(row)

                    js["context"] = ""
                    js["assistant"] = "I couldn't found any relevant information."

                    print(js)

                    with open(OUTPUT_FILE, "a") as f:
                        f.write(str(js) + "\n")

                    i += 1

            except Exception as e:
                pass


def create_wrong_context_responses():
    i = 0
    previous_context = ""

    with open(OUTPUT_FILE, "r") as file:
        for index, row in enumerate(set(file.readlines())):
            try:
                if i < 200:
                    row = row.replace("'", '"')
                    js = json.loads(row)

                    actual_context = js["context"]

                    js["context"] = previous_context
                    js["assistant"] = (
                        "Unfortunately we don't have this product or book."
                    )

                    previous_context = actual_context

                    if previous_context != "" and i > 100:
                        print(js)
                        with open(OUTPUT_FILE, "a") as f:
                            f.write(str(js) + "\n")

                    i += 1

            except Exception as e:
                pass

    print(i)


create_jsonl_from_csv()
create_no_context_responses()
create_wrong_context_responses()
