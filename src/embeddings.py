"""
# Schema Embedding and Storage Module

This module is responsible for generating embeddings from a schema file using
Google's Generative AI Embeddings and storing them in a Chroma vector store
for efficient retrieval.
"""

import os
from uuid import uuid4
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document  # Import Document class
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

SCHEMA_FILE = "schema.txt"

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=gemini_api_key,
    task_type="retrieval_document",
)


# Function to generate embeddings
def generate_embeddings(file_path):
    """
    ### `generate_embeddings(file_path: str) -> list | None`
    Reads a schema file, extracts individual table definitions,
    and generates embeddings for each table using the Google Generative AI embedding model.

    **Parameters:**
    - `file_path (str)`: Path to the schema file containing table definitions.

    **Returns:**
    - `list[dict] | None`: A list of dictionaries, each containing:
    - `"document"`: The extracted table schema.
    - `"embedding"`: Corresponding embedding vector.
    - Returns `None` if an error occurs.
    """
    try:
        # Read the schema file
        with open(file_path, "r") as f:
            schema_content = f.read()

        # Assuming each table starts with 'Table Name:'
        tables = schema_content.split("Table Name:")[1:]
        tables = [
            f"Table Name:{table.strip()}" for table in tables
        ]  # Re-add 'Table Name:'

        # Generate embeddings for each table and store them
        embeddings_list = []
        for table in tables:
            table_embedding = embeddings.embed_documents([table])[
                0
            ]  # Ensure we get the embedding for the table
            embeddings_list.append({"document": table, "embedding": table_embedding})

        return embeddings_list
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None


# Generate embeddings for the schema
schema_embeddings = generate_embeddings(SCHEMA_FILE)

# Print the embeddings and store them in Chroma
if schema_embeddings:
    print("Schema Embeddings:")
    print(schema_embeddings)

    # Create Chroma vector store
    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",
    )

    # Generate unique IDs for the documents
    uuids = [str(uuid4()) for _ in range(len(schema_embeddings))]

    # Prepare the documents as langchain Document objects
    documents = [
        Document(page_content=embedding_data["document"])
        for embedding_data in schema_embeddings
    ]
    embeddings_list = [
        embedding_data["embedding"] for embedding_data in schema_embeddings
    ]

    # Add each embedding to the Chroma collection using add_documents method
    vector_store.add_documents(
        documents=documents, embeddings=embeddings_list, ids=uuids
    )

    print("Embeddings have been stored in Chroma.")
else:
    print("Failed to generate and store schema embeddings.")
