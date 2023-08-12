import logging
from chromadb.config import Settings
from langchain.vectorstores import Chroma

def get_chroma_settings(database_name):
    """
    This function returns the chroma settings for a given database name.

    Args:
        database_name (str): The name of the database.

    Returns:
        Settings: The chroma settings object.
    """
    chroma_directory = constants.CHROMA_DIRECTORY.format(database_name=database_name)
    return Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=chroma_directory,
        anonymized_telemetry=False
    )
# Import necessary modules
import logging
from chroma import Chroma
import constants

def get_database(embeddings, database_name, collection_name=Chroma._LANGCHAIN_DEFAULT_COLLECTION_NAME):
    # Set up Chroma database
    db = Chroma(
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        embedding_function=embeddings,
        client_settings=get_chroma_settings(database_name),
    )

    # Log the number of chunks in the datastore
    logging.debug(f"There are {len(db.get()['documents'])} chunks in the datastore")

    # Return the Chroma database
    return db

# Note: Unused functions and variables should be evaluated in the larger code base.
# Import necessary modules
import logging
from chroma import Chroma
import constants

def store_embeddings(embeddings, documents, database_name):
    # Create a Chroma object with the given documents and embeddings
    db = Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        client_settings=get_chroma_settings(database_name),
    )

    # Log a debug message
    logging.debug("Persisting DB")

    # Persist the Chroma object
    db.persist()

    # Set the Chroma object to None to release memory
    db = None