import logging
from chromadb.config import Settings
from langchain.vectorstores import Chroma

def get_chroma_settings(database_name):
    return Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        anonymized_telemetry=False
    )

def get_database(embeddings, database_name, collection_name = Chroma._LANGCHAIN_DEFAULT_COLLECTION_NAME):

    db = Chroma(
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),        
        embedding_function=embeddings,
        client_settings=get_chroma_settings(database_name),
    )

    logging.debug(f"There are {len(db.get()['documents'])} chunks in the datastore")

    return db 

def store_embeddings(embeddings, documents, database_name):   

    db = Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=constants.CHROMA_DIRECTORY.format(database_name=database_name),
        client_settings=get_chroma_settings(database_name),
    )

    logging.debug("Persisting DB")
    db.persist()
    db = None
