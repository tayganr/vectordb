import argparse
from tabulate import tabulate
from utils.search import query_search_index
from utils.openai import generate_query_embedding

# Define the ANSI escape codes for coloured text
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--query", help="the search query", required=True)
parser.add_argument("-n", "--num-neighbors", type=int, default=3, help="the number of nearest neighbors to retrieve")
args = parser.parse_args()

# Define the search query
query = args.query
number_of_nearest_neighbors = args.num_neighbors
print(f"\nLooking for the {ORANGE}{number_of_nearest_neighbors}{RESET} nearest neighbors of '{ORANGE}{query}{RESET}' in the vector space...\n")

# Generate the query embedding
embedding = generate_query_embedding(query)
results = query_search_index(embedding, number_of_nearest_neighbors)["value"]

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
