
import json
import logging
from datetime import datetime
from typing import Union, List, Dict
from enum import Enum

from dotenv import dotenv_values
import openai

from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from code_reviewer_configuration import CodeReviewerConfiguration
from refactor.prompts import REFACTOR_PROMPT, REFACTOR_TEMPLATE, SUMMARIZE_PROMPT, SUMMARIZE_TEMPLATE
from utilities.token_helper import simple_get_tokens_for_message
from utilities.open_ai import get_openai_api_key

# Supported file types for refactoring
SUPPORTED_FILE_TYPES = {
    "py": Language.PYTHON,
    "cpp": Language.CPP,
}


class CodeRefactor:
    def __init__(self, configuration: CodeReviewerConfiguration):
        self.configuration = configuration
        self.llm_arguments_configuration = configuration.llm_arguments

        # Calculate remaining tokens for prompt
        self.remaining_prompt_tokens = (
            self.llm_arguments_configuration.max_supported_tokens
            - self.llm_arguments_configuration.max_completion_tokens
            - simple_get_tokens_for_message(REFACTOR_TEMPLATE)
        )

        # Initialize language model
        self.llm = ChatOpenAI(
            model=self.llm_arguments_configuration.model,
            temperature=self.llm_arguments_configuration.temperature,
            openai_api_key=get_openai_api_key(),
            max_tokens=self.llm_arguments_configuration.max_completion_tokens,
        )

        # Initialize refactoring and summarizing chains
        self.refactor_chain = LLMChain(llm=self.llm, prompt=REFACTOR_PROMPT)
        self.summarize_chain = LLMChain(llm=self.llm, prompt=SUMMARIZE_PROMPT)

    def refactor(self, target_files: List[str]):
        # Add target files to datastore and get vector database
        vector_db = self.add_to_datastore(target_files, self.remaining_prompt_tokens)

        documents = vector_db.get()
        num_documents = len(documents["documents"])

        logging.info(f"Created vector database with {num_documents} chunks of code")

        # TODO: Add this step in later
        # First summarize the code's functionality
        # for i in range(0, num_documents):
        #     logging.info(
        #         f"Refactoring {documents['metadatas'][i]['file_name']}"
        #     )
        #     code_to_refactor = documents["documents"][i]

        #     # Summarize the chunk
        #     if self.configuration.include_summary:
        #         chunk_summary = self.summarize_chunk(
        #             code_to_refactor
        #         )
        #         documents["metadatas"][i]["summary"] = chunk_summary

        # Refactor the code
        for i in range(num_documents):
            logging.info(f"Refactoring {documents['metadatas'][i]['file_name']}")
            code_to_refactor = documents["documents"][i]

            documents["metadatas"][i]["refactored_code"] = self.refactor_chain(
                inputs={
                    "code": code_to_refactor,
                    "language": documents["metadatas"][i]["language"],
                }
            )["text"]

        return documents

    def add_to_datastore(self, target_files: List[str], max_split_size: int) -> Chroma:
        documents = []
        for file in target_files:
            logging.debug(f"Looking at {file}")

            # Get the file extension
            file_extension = file.split(".")[-1]

            # If we support it, continue, otherwise skip it
            if file_extension not in SUPPORTED_FILE_TYPES:
                logging.debug(
                    f"Skipping {file} because it is not a supported file type"
                )
                continue

            language = SUPPORTED_FILE_TYPES[file_extension]
            logging.info(f"Language is {language} for {file}")

            # Read the file in
            with open(file, "r") as f:
                file_contents = f.read()

            # Split the code into chunks
            code_splitter = RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=max_split_size,
                chunk_overlap=0,
                keep_separator=True,
                add_start_index=True,
                length_function=simple_get_tokens_for_message,
            )

            # Create documents from the chunks
            joined_docs = code_splitter.create_documents([file_contents])

            for d in joined_docs:
                d.metadata = {"file_name": file, "language": language}
                documents.append(d)

        return Chroma.from_documents(documents, OpenAIEmbeddings())

