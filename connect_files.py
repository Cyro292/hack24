from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
client = OpenAI()

files = client.files.list()

file_ids = [f.id for f in files.data]


def create_assistant_file(i, id):
    try:
        # assistant_file = client.beta.assistants.files.create(
        #     assistant_id="asst_lDEntqOlH9CL6J7QKcdDgl3Q",
        #     file_id=id
        # )

        client.files.delete(id)

        print(i)
    except Exception as e:
        print(e)


# Use ThreadPoolExecutor to parallelize file creation
with ThreadPoolExecutor(max_workers=15) as executor:
    # Create a list of all arguments for each task
    tasks = [(i, id) for i, id in enumerate(file_ids)]

    # Use map to execute the function in parallel, passing the arguments
    results = executor.map(lambda args: create_assistant_file(*args), tasks)
