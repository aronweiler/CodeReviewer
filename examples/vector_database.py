import logging
from chromadb.config import Settings
from langchain.vectorstores import Chroma

# Constants are not defined in this code snippet. Assuming they are defined elsewhere in the codebase.
# If not, they should be defined before being used.

# Function to get the settings for Chroma database
def get_chroma_settings(database_name):
    return Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        anonymized_telemetry=False
    )

# Function to get the Chroma database
def get_database(embeddings, database_name, collection_name=Chroma._LANGCHAIN_DEFAULT_COLLECTION_NAME):
    # Create a Chroma instance with the given settings
    db = Chroma(
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        embedding_function=embeddings,
        client_settings=get_chroma_settings(database_name),
    )

    # Log the number of chunks in the datastore
    logging.debug(f"There are {len(db.get()['documents'])} chunks in the datastore")

    return db

# Function to store embeddings in the Chroma database
def store_embeddings(embeddings, documents, database_name):
    # Create a Chroma instance from documents with the given settings
    db = Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        client_settings=get_chroma_settings(database_name),
    )

    # Log the persistence of the database
    logging.debug("Persisting DB")
    db.persist()

    # Explicitly setting db to None to ensure that the memory is freed
    # This is not necessary in Python as the garbage collector will automatically free the memory
    # when there are no more references to the object. However, it can be a good practice in long-running
    # programs to explicitly free memory when it is no longer needed.
    db = None
