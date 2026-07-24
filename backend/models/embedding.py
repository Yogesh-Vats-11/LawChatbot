import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import BNS_PATH

with open(BNS_PATH, "r", encoding="utf-8") as f:
    bns_data = json.load(f)

sections = []
texts = []

for law in bns_data:
    text = f"""
    Section {law['section_number']}
    Title: {law['section_title']}
    Content: {law['content']}
    """
    sections.append(law)
    texts.append(text)

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

embeddings = model.encode(texts)
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))