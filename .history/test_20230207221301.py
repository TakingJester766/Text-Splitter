import pinecone
from datasets import load_dataset
from tqdm.auto import tqdm
import openai
import sys
paragraphs = []
file_path = "book.txt"
sys.setrecursionlimit(10000)
paragraphs = []

def create_text_string(file_path):
    with open(file_path, "r") as file:
        contents = file.read()
        complete_text = contents
        return complete_text

def split_file_into_array(file_path, arr):
    with open(file_path, "r") as file:
        contents = file.read()
        lines = contents.split("\n")
    arr.extend([line for line in lines if line.endswith(".") or line.endswith("!") or line.endswith("?")])        

def extract_paragraphs(text, arr, paragraphs):
    if not arr:
        return

    text_to_add = text.split(arr[0], 1)[0]
    text_to_add += arr[0]
    paragraphs.append(text_to_add)

    start_index = text.index(text_to_add) + len(text_to_add)
    new_text = text[start_index:]
    new_arr = arr[1:]

    extract_paragraphs(new_text, new_arr, paragraphs)

arr = []
text = create_text_string(file_path)
split_file_into_array(file_path, arr)

text = extract_paragraphs(text, arr, paragraphs)

with open("config.txt", "r") as file:
    config_str = file.readlines()

openai.api_key = config_str[0].strip()
openai.organization = config_str[1].strip()

#openai.Engine.list()

MODEL = "text-embedding-ada-002"

res = openai.Embedding.create(
    input=[
        "This is a test",
        "This is another test",
        "This is a third test"
    ], engine=MODEL
)

#print(res)

embeds = [record['embedding'] for record in res['data']]

pinecone.init(
    api_key="e1104cee-b201-44e4-9db4-bc3eaf0d64ad",
    environment="us-east1-gcp",
)

if 'openai' not in pinecone.list_indexes():
    pinecone.create_index('openai', dimension=len(embeds[0]))

index = pinecone.Index('openai')

trec = load_dataset('trec', split='train[:1000]')

count = 0
batch_size = 32
for i in tqdm(range(0, len(trec), batch_size)):
    i_end = min(i+batch_size, len(trec['text']))
    lines_batch = trec['text'][i: i+ i_end]
    ids_batch = [str(n) for n in range(i, i_end)]
    
    res = openai.Embedding.create(input=lines_batch, engine=MODEL)
    embeds = [record['embedding'] for record in res['data']]
    meta = [{'text': line} for line in lines_batch]
    to_upsert = zip(ids_batch, embeds, meta)
    index.upsert(vectors=list(to_upsert))

# querying

query = "What caused the 1929 Great Depression?"

xq = openai.Embedding.create(input=[query], engine=MODEL)['data'][0]['embedding']

res = index.query(xq, top_k=5, include_metadata=True)
#print(res)

for match in res['matches']:
    print(f"{match['score']:.2f}: {match['metadata']['text']}")

