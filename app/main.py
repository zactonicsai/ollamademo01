from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

app = FastAPI(title="FastAPI Chroma Embedder")

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection("fastapi_rest_snippets", embedding_function=embedding_fn)

class Query(BaseModel):
    query: str

@app.post("/query")
def query_snippets(q: Query):
    res = collection.query(query_texts=[q.query], n_results=3)
    return res
