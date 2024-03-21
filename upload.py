from openai import OpenAI
import os
client = OpenAI()

files = os.listdir('data')
file_ids = []

for i, file in enumerate(files):
    try:
        id = client.files.create(
            file=open('data/'+file, "rb"),
            purpose="assistants"
        )
        file_ids.append(id)

        print(i, id)
    except Exception as e:
        print(e)
        continue

print(file_ids)

# assistant_file = client.beta.assistants.files.create(
#   assistant_id="asst_lDEntqOlH9CL6J7QKcdDgl3Q",
#   file_id="file-abc123"
# )
# print(assistant_file)
