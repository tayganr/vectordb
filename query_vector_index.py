from tabulate import tabulate
from utils.search import query_search_index
from utils.openai import generate_query_embedding

# Define the ANSI escape codes for coloured text
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"

# Define the search query
query = "fit for purpose"
print(f"Querying the search index for the nearest neighbors to the vector representation of '{ORANGE}{query}{RESET}'...\n")

# Generate the query embedding
embedding = generate_query_embedding(query)
results = query_search_index(embedding)["value"]

# Define a custom formatting function to truncate the text in the "content" column
def truncate_title(text):
    max_length = 50
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text

# Apply the custom formatting function to the "content" column
for result in results:
    result["content"] = truncate_title(result["content"])

# Print the results in a tabulated format
print(tabulate(results, headers="keys", tablefmt="grid"))
