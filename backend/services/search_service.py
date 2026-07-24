import numpy as np
from models.embedding import model, index, sections

def semantic_search(query, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)
    return [sections[i] for i in indices[0]]