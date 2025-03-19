from datasets import load_dataset

dataset = load_dataset(
    "csv", data_files="fase-03/data/trn-processed.csv", split="train"
)

print(len(dataset))

# seleciona 1000 aleatorios
dataset = dataset.shuffle(seed=42).select(range(1000))

# salva o csv, sobrescrevendo o arquivo
dataset.to_csv("fase-03/data/sample.csv", index=False)
