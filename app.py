import base64
import os
import tempfile
import json
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.search import query_search_index
from utils.openai import generate_query_embedding
from chat import evaluate_snippet
import pandas as pd

# Configuration variables
FILE_TYPE_PDF = "pdf"
MINIMUM_CHUNK_LENGTH = 100

def main():
    # Heading
    st.title("Multi-Class Classification with OpenAI and Vector Search")

    # Create a file upload widget
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    # If a file was uploaded
    if uploaded_file is not None:
        # Get the file data as a bytes object
        file_data = uploaded_file.read()

        # Save the file data to a temporary PDF file
        temp_pdf_file_path = save_to_temp_file(file_data)

        # Load the PDF file
        document = load_pdf(temp_pdf_file_path)

        chunks = split_text(document)

        # Define a list to store the chunks
        table = []

        # Loop through the chunks and display them
        with st.spinner("Processing chunks..."):
            progress_bar = st.progress(0)
            # Create an empty placeholder
            text = st.empty()
            for i, chunk in enumerate(chunks):
                # Update the progress bar
                progress_bar.progress((i + 1) / len(chunks))

                # Update the text message
                message = "Processing Chunk {} of {}...".format(i + 1, len(chunks))
                text.write(message)

                row = process_chunk(i, chunk)
                table.append(row)
            
            # Empty the placeholder
            text.empty()

            # Convert the chunks to a DataFrame
            df = pd.DataFrame(table)

            # Add a button to export the table to CSV
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="chunks.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

            #  Render PDF
            pdf_download_link = get_pdf_download_link(temp_pdf_file_path)

            with open(temp_pdf_file_path, "rb") as f:
                contents = f.read()
                data_url = base64.b64encode(contents).decode("utf-8")
                pdf_embed = f'<object type="application/pdf" data="data:application/pdf;base64,{data_url}" width="700" height="1000"></object>'

            st.markdown(pdf_download_link, unsafe_allow_html=True)
            st.markdown(pdf_embed, unsafe_allow_html=True)

def get_pdf_download_link(pdf_file_path):
    with open(pdf_file_path, "rb") as f:
        contents = f.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{data_url}" download="downloaded_file.pdf">Download PDF</a>'
        return href

def process_chunk(i, chunk):
    # 1. OpenAI - Generate the query embedding
    snippet = chunk["chunk"]
    embedding = generate_query_embedding(snippet)

    # 2. Cognitive Search - Query the search index
    query_results = query_search_index(embedding, 1)
    commitment = query_results["value"][0]["category"]

    # Get the policy and examples for the commitment
    examples_doc = get_examples_doc()
    policy = examples_doc[commitment]["policy"]
    examples = examples_doc[commitment]["examples"]

    # 3. OpenAI - Evaluate the snippet
    eval = evaluate_snippet(commitment, policy, examples, snippet)
    is_special_commitment, confidence, reason, eval = unpack_eval(eval)

    # Display the chunk
    row = {
        "chunk_number": i,
        "page_number": chunk["page_number"]+1,
        "snippet": snippet,
        "commitment": commitment,
        "is_special_commitment": is_special_commitment,
        "confidence": confidence,
        "reason": reason,
        "eval": eval
    }
    return row

def unpack_eval(eval):
    if isinstance(eval, str):
        try:
            eval = json.loads(eval)
        except json.JSONDecodeError:
            return None, None, None, eval

    is_special_commitment = eval.get("is_special_commitment")
    if isinstance(is_special_commitment, str):
        is_special_commitment = is_special_commitment.upper()

    confidence = eval.get("confidence")
    if isinstance(confidence, str):
        confidence = confidence.upper()

    reason = eval.get("reason")

    return is_special_commitment, confidence, reason, eval

def get_examples_doc():
    # Load the examples from from messages/examples.json and return the dictionary
    with open(os.path.join(os.path.dirname(__file__), "messages", "examples.json"), "r") as f:
        examples = json.load(f)
    return examples

def save_to_temp_file(file_data):
    # Create a temporary file to write the uploaded file data to
    with tempfile.NamedTemporaryFile(suffix=f".{FILE_TYPE_PDF}", delete=False) as temp_file:
        temp_file.write(file_data)

    # Get the full path of the temporary file
    temp_file_path = os.path.abspath(temp_file.name)

    return temp_file_path

def load_pdf(file_path):
    # Create a PDF loader object
    loader = PyPDFLoader(file_path)

    # Load the PDF file
    document = loader.load()

    return document

def split_text(document):
    # Concatenate the page content of all documents into one variable
    text = ""
    page_indicator_prefix = "[METADATA]PAGE:"
    page_indicator_suffix = ":"
    for page in document:
        text += page_indicator_prefix + str(page.metadata["page"]) + page_indicator_suffix + "\n\n"
        text += page.page_content

    # Create a text splitter object
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    # Split the text into chunks
    chunks = splitter.split_text(text)

    # Loop through the chunks and extract the page number
    current_page_number = None
    chunks_with_page_numbers = []
    for i, chunk in enumerate(chunks):
        chunk_dict = {}
        # Check if the chunk contains a page number tag
        if page_indicator_prefix in chunk:
            # Extract the page number from the tag
            page_number = int(chunk.split(page_indicator_prefix)[1].split(page_indicator_suffix)[0])

            # Update the current page number
            current_page_number = page_number

            # Remove the page number tag from the chunk
            chunk = chunk.replace(f"{page_indicator_prefix}{page_number}{page_indicator_suffix}", "")
            chunk = chunk.strip()

        # Add the chunk and the page number to the list if the chunk length is greater than the minimum length
        if len(chunk) > MINIMUM_CHUNK_LENGTH:
            chunk_dict["chunk"] = chunk
            chunk_dict["page_number"] = current_page_number
            chunks_with_page_numbers.append(chunk_dict)

    return chunks_with_page_numbers

if __name__ == "__main__":
    main()
