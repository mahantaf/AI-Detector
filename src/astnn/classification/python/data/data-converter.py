import pandas as pd

data_file = 'mbpp_chatgpt_python_merged.csv'

df = pd.read_csv(data_file)
df['label'] = df['label'].replace({'human': 1, 'lm': 2})
df.to_pickle('programs.pkl')