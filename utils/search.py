import requests
import json
import configparser

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get values from the config file
index_name = config.get('search', 'index_name')
search_service_name = config.get('search', 'search_service_name')
search_api_key = config.get('search', 'search_api_key')

# Define the ANSI escape codes for coloured text
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"

# Define the variable values
search_api_version = "2023-07-01-Preview"
search_headers = {"Content-Type": "application/json", "api-key": search_api_key}
base_url = f"https://{search_service_name}.search.windows.net"


def query_search_index(embedding):
    # Define the REST API endpoints
    url = f"{base_url}/indexes/{index_name}/docs/search?api-version={search_api_version}"

    # Define the request body
    request_body = {
        "vector": {
            "value": embedding,
            "fields": "contentVector",
            "k": 3
        },
        "select": "content, category"
    }

    # Query the search index
    response = requests.post(url, headers=search_headers, json=request_body)
    return response.json()

def create_search_index():
    # Define the REST API endpoints
    url = f"{base_url}/indexes/{index_name}?api-version={search_api_version}"

    # Define the request body
    request_body = {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "content","type": "Edm.String","searchable": True,"retrievable": True},
            {"name": "category","type": "Edm.String","filterable": True,"searchable": True,"retrievable": True},
            {"name": "contentVector","type": "Collection(Edm.Single)","searchable": True,"retrievable": True,"dimensions": 1536,"vectorSearchConfiguration": "my-vector-config"}
        ],
        "corsOptions": {"allowedOrigins": ["*"],"maxAgeInSeconds": 60},
        "vectorSearch": {"algorithmConfigurations": [{"name": "my-vector-config","kind": "hnsw","hnswParameters": {"m": 4,"efConstruction": 400,"efSearch": 500,"metric": "cosine"}}]},
        "semantic": {"configurations": [{"name": "my-semantic-config","prioritizedFields": {"prioritizedContentFields": [{"fieldName": "content"}],"prioritizedKeywordsFields": [{"fieldName": "category"}]}}]}
    }

    # Create the search index
    response = requests.put(url, headers=search_headers, json=request_body)
    if response.status_code == 201:
        print(f"Index {ORANGE}{index_name}{RESET} {BLUE}created{RESET}.")
    else:
        print(f"Error creating index {index_name}: {response.text}")

def delete_search_index():
    # Define the REST API endpoints
    url = f"{base_url}/indexes/{index_name}?api-version={search_api_version}"

    # Delete the search index if it exists
    response = requests.get(url, headers=search_headers)
    if response.status_code == 200:
        # Index exists, delete it
        print(f"Index {ORANGE}{index_name}{RESET} exists.")
        response = requests.delete(url, headers=search_headers)
        if response.status_code == 204:
            print(f"Index {ORANGE}{index_name}{RESET} {RED}deleted{RESET}.")
        else:
            print(f"Error deleting index {index_name}: {response.text}")
    else:
        print(f"Index {ORANGE}{index_name}{RESET} does not exist.")

def upload_documents_to_search_index(payload):
    # Define the list of documents to upload
    url = f"{base_url}/indexes/{index_name}/docs/index?api-version={search_api_version}"

    # Call the upload docs endpoint
    try:
        response = requests.post(url, headers=search_headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        print(f"Documents {GREEN}uploaded{RESET} successfully.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error uploading documents: {e}")
