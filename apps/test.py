import pandas as pd

data = pd.read_csv('Analysing-Sensitive-Speech/outputs/data/time_elapsed.csv',encoding="utf-8")
print(data.iloc[:10])
