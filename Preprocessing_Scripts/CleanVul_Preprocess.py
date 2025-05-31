# Forked from Oh Taebin's code

import numpy as np
import pandas as pd
from transformers import AutoTokenizer
import random
import json

df = pd.read_csv("/content/CleanVul_vulnscore_4.csv")

df_lang = df[df['extension'].isin(['c', 'cpp'])].copy()


tokenizer = AutoTokenizer.from_pretrained("t5-base")

def token_count(text):
    return len(tokenizer.tokenize(text))


df_lang['token_length'] = df_lang['func_before'].apply(token_count)

df_filtered = df_lang[(df_lang['token_length'] >= 128) & (df_lang['token_length'] <= 2048)]

dataset = []

rand_list = random.sample(range(1000, 3601), 800)

i = 0
for code in df_filtered['func_before']:
    data = {
            "instruction": "Check if the following code has vulnerabilities.",
            "input": code,
            "output": "1",
            "idx": rand_list.pop()
    }
    dataset.append(data)
    i += 1
    if i == 300:
      break

i = 0
for code in df_filtered['func_after']:
    data = {
            "instruction": "Check if the following code has vulnerabilities.",
            "input": code,
            "output": "0",
            "idx": rand_list.pop()
    }
    dataset.append(data)
    i += 1
    if i == 300:
      break


path = "Cleanvul_Processed_Dataset.jsonl"

with open(path, 'w', encoding='utf-8') as f:
    for item in dataset:
        json_line = json.dumps(item, ensure_ascii=False)
        f.write(json_line + '\n')