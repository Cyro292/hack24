import pandas as pd
import os
import json
import re

aggregated_data = pd.read_csv('aggregated_data.csv')

# Convert the DataFrame to a JSON representation
data_json = aggregated_data.to_json(orient='records')
# Load the JSON data into a Python list of dictionaries
data_list = json.loads(data_json)


texts = {}

for t in data_list:
    cleaned_string = re.sub(r'[^a-zA-Z0-9 .,;\'"-]',
                            '', t['paragraphs'])
    cleaned_string = cleaned_string.translate(str.maketrans('', '', "\"',"))

    print(t['filepath'].split(os.sep)[0])
    key = t['filepath'].split(os.sep)[0]

    if not texts.get(key):
        texts[key] = cleaned_string
    else:
        texts[key] += ' ' + cleaned_string


for k, v in texts.items():
    with open('data/'+k+'.txt', 'w') as f:
        f.write(v)
