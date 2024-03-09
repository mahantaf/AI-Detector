import pandas as pd

data_file = 'humaneval_chatgpt_java_merged.csv'

df = pd.read_csv(data_file)
df['label'] = df['label'].replace({'human': 1, 'lm': 2})
df.to_pickle('programs.pkl')