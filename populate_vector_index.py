import json
from utils.search import create_search_index, delete_search_index, upload_documents_to_search_index
from utils.openai import generate_query_embedding

try:
    # 1. Drop search index if it exists
    delete_search_index()

    # 2. Create search index
    create_search_index()

    # 3. Generate embeddings
    with open('data/documents.json', 'r') as f:
        documents = json.load(f)

    embeddings = []
    print("Generatting embeddings...")
    for i, document in enumerate(documents):
        embedding = generate_query_embedding(document["content"])
        embeddings.append(embedding)
        print(f" - Embedding {i+1} of {len(documents)} generated.")

    # 4. Upload documents to search index
    data = []
    for i in range(len(documents)):
        document = {
            "id": str(i+1),
            "content": documents[i]["content"],
            "category": documents[i]["category"],
            "contentVector": embeddings[i]
        }
        data.append(document)
    payload = {
        "value": data
    }
    upload_documents_to_search_index(payload)

except Exception as e:
    print(f"Error: {e}")
