import openai
import os, csv
import pandas as pd
import numpy as np
from openai import OpenAI
from tqdm import tqdm

os.environ['OPENAI_API_KEY'] = ''
openai.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

file_name = 'mbpp_chatgpt_python'
print(file_name)
dataset, model, lang = file_name.split('_')

df = pd.read_csv(f'', index_col=0)
output_csv = open(f'', 'w')
output_writer = csv.writer(output_csv, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
output_writer.writerow(['idx', 'code', 'label', 'pred'])

codes = df['code'].tolist()
labels = df['actual label'].tolist()

pred_list = []
label_list = []

for i in tqdm(range(len(codes))):
    code = codes[i]
    label = labels[i]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You will be provided with a {lang} source code snippet. Please determine if the source code is generated by Artificial intelligence (AI) models (i.e. language models) or human. If the code is generated by human, label it as 1. If the code is generated by AI, label is a 0. Return the label only in the output."},
            {"role": "user", "content": f"Determine whether this code is generated by human or AI and return the label."},
            {"role": "user", "content": f"Code:\n{str(code)}"}
        ]
    )

    pred = response.choices[0].message.content
    pred_list.append(pred)
    label_list.append(label)
    output_writer.writerow([i, code, label, pred])