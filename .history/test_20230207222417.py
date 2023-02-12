import pinecone
from datasets import load_dataset
from tqdm.auto import tqdm
import openai

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

trec = load_dataset('trec', split='train[:5000]')

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

