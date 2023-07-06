# Multi-Class Classification with OpenAI and Vector Search

## Pre-Requisites

* Azure OpenAI
  * Embedding Model (text-embedding-ada-002)
  * Chat Model (gpt-35-turbo)
* Azure Cognitive Search

## Setup

1. Clone the repository.
1. Create a Python virtual environment `python3 -m venv env`.
1. Install Python depencies `pip install -r requirements.txt`.
1. Rename `config.ini.template` to `config.ini`.
1. Update the variables within `config.ini` based on your values from the Azure portal.
1. Rename `documents.json.template` to `documents.json`. Update the contents of the JSON file with `category` and `content` pairs to pre-populate the vector database.
1. Create a chat API messages template beneath a folder called `messages`. Note: See `messages.json` as an example structure.

## Usage

* `populate_vector_index.py` - Running this script will drop/create a vector search index in Azure Cognitive Search based on the documents within `documents.json`.
* `query_vector_index.py --query "YOUR_QUERY"` - Running this script will query the populated vector database for the nearest neighbors.
* `classify_text_snippet.py --snippet "YOUR_SNIPPET"` - Running this script will use the chat completion API to classify the snippet.
