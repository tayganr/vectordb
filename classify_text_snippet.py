import argparse
import json
from tabulate import tabulate
from utils.openai import generate_chat_completion

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--snippet", help="the new snippet of text to classify", required=True)
args = parser.parse_args()

# Load the message template
with open("messages/fitness.json", "r") as f:
    messages = json.load(f)

# Define the new dictionary to append to the list of dictionaries
new_dict = {"role": "user", "content": args.snippet}

# Append the new dictionary to the list of dictionaries in the message template
messages.append(new_dict)

# Generate the chat completion using the message template
chat_response = generate_chat_completion(messages)

try:
    # Try to access the "content" key in the expected dictionary structure
    content = chat_response["choices"][0]["message"]["content"]
except (KeyError, IndexError):
    # Handle the case where neither dictionary structure is valid
    content = None
    print("Error: could not extract content from chat response")

if content is not None:
    try:
        # Attempt to parse the JSON-formatted text into a Python dictionary
        data = json.loads(content)
    except json.JSONDecodeError:
        # Handle the case where the content is not valid JSON
        data = None
        print("Error: content is not valid JSON")
        print(content)

if data is not None:
    # Truncate the "reason" column to a maximum of 150 characters
    data ["reason"] = (data ["reason"] [:150] + '..') if len (data ["reason"]) > 50 else data ["reason"]

    # Extract the keys from the dictionary
    keys = list(data.keys())

    # Extract the values from the dictionary
    values = list(data.values())

    # Format the values as a list of lists
    table_data = [values]

    # Format the list of lists as a table using the tabulate library
    table_str = tabulate(table_data, headers=keys)

    # Print the table
    print("\n")
    print(table_str)
