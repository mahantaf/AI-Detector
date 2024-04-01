import openai
import os
from openai import OpenAI
import json
import pandas as pd

def create_dataset(question, answer):
    return {
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }

input_dir = ''

for folder_name in os.listdir(input_dir):
    for file_name in os.listdir(input_dir+folder_name):
        print(file_name)
        dataset_name, model_name, lang, split, temp, _ = file_name.split('_')
        source_file_name = '_'.join([dataset_name, model_name, lang])

        if not os.path.exists(f''):
            os.mkdir(f'')

        DEFAULT_SYSTEM_PROMPT = f'You will be provided with a {lang} source code. Please determine if the source code is generated by Artificial intelligence (AI) models (i.e. language models) or human. If the code is generated by human, output 1. If the code is generated by AI, output 0. Return the label only in the output.'
        df = pd.read_csv(input_dir+folder_name+'/'+file_name, index_col=0)
        with open(f"", 'w') as f:
            for _, row in df.iterrows():
                example_str = json.dumps(create_dataset(f"Determine whether the source code is generated by human or AI and return the label.\nCode:\n{str(row['code'])}", str(row['actual label'])))
                f.write(example_str+'\n')
