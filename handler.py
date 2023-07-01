import json
from utils.search import create_search_index, delete_search_index, upload_documents_to_search_index
from utils.openai import generate_query_embedding

try:
    # 1. Drop search index if it exists
    delete_search_index()

    # 2. Create search index
    create_search_index()

    # 3. Generate query embeddings
    with open('data/documents.json', 'r') as f:
        documents = json.load(f)

    query_embeddings = [generate_query_embedding(document=document, snippet_number=i+1, total_snippets=len(documents)) for i, document in enumerate(documents)]

    # 4. Upload documents to search index
    upload_documents_to_search_index(documents, query_embeddings)

except Exception as e:
    print(f"Error: {e}")