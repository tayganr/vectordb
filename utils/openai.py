import requests
import configparser

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get values from the config file
openai_api_key = config.get('openai', 'api_key')
openai_service_name = config.get('openai', 'openai_service_name')
openai_deployment_name = config.get('openai', 'openai_deployment_name')

# Define the variable values
openai_api_version = "2023-05-15"
openai_headers = {"Content-Type": "application/json", "api-key": openai_api_key}
base_url = f"https://{openai_service_name}.openai.azure.com"

def generate_query_embedding(input):
    # Define the REST API endpoint
    query_embedding_url = f"{base_url}/openai/deployments/{openai_deployment_name}/embeddings?api-version={openai_api_version}"

    # Define the request body
    request_body = {
        "input": input
    }

    # Generate the query embedding
    try:
        response = requests.post(query_embedding_url, headers=openai_headers, json=request_body, timeout=10)
        response.raise_for_status()
        # Parse the response body as JSON
        query_embedding_response = response.json()
        # Get the embedding from the response
        query_embedding = query_embedding_response["data"][0]["embedding"]
        return query_embedding
    except requests.exceptions.RequestException as e:
        print(f"Error generating query embedding: {e}")
        return None
