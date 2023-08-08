from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
from dotenv import dotenv_values, load_dotenv
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
import logging
from datetime import datetime
from typing import Union, List, Dict
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from llm_arguments import LLMArguments
from prompts import REVIEW_PROMPT, REVIEW_TEMPLATE
from token_helper import simple_get_tokens_for_message


class CodeReviewer:
    def __init__(self, llm_arguments_configuration: LLMArguments):
        self.llm_arguments_configuration = llm_arguments_configuration

        self.remaining_prompt_tokens = (
            self.llm_arguments_configuration.max_supported_tokens
            - self.llm_arguments_configuration.max_completion_tokens
            - simple_get_tokens_for_message(REVIEW_TEMPLATE)
        )

        self.llm = ChatOpenAI(
            model=llm_arguments_configuration.model,
            temperature=llm_arguments_configuration.temperature,
            openai_api_key=self.get_openai_api_key(),
            max_tokens=llm_arguments_configuration.max_completion_tokens,
        )

        self.db = Chroma(OpenAIEmbeddings())

        self.chain = LLMChain(llm=self.llm, prompt=REVIEW_PROMPT)

    def review(self, target_files: List[str]):
        # Iterate through the files, and do several things:
        # - Read the file
        # - Split the files into chunks of (max_tokens - max_completion_tokens)
        # - Create embeddings of each chunk so that the LLM can search for them
        # - Create an in-memory database of the file chunks and embeddings for later reference by the LLM

        for file in target_files:
            loader = TextLoader(file)
            document = loader.load()

            self.split_and_add_to_datastore(document)

        # Once the files are split and added to the datastore, we can start the review process
        
            

    def split_and_add_to_datastore(self, document:Document):
        # Split the file into chunks of (max_tokens - max_completion_tokens)
        # This is because the LLM will need to add the completion tokens to the end of the chunk

        # If the size is small enough to fit in one call to the LLM, just add the file contents
        if simple_get_tokens_for_message(document.page_content) <= self.remaining_prompt_tokens:
            self.db.add_documents([document])
        else:
            # Otherwise, split the file into chunks.
            # TODO: Tune chunk size for optimal effectiveness, and make configurable
            # TODO: Add support for different language parsers so that I can effectively split on functions, classes, etc.
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.remaining_prompt_tokens,
                chunk_overlap=0,
                separators=["\n\n", "\r\n"],
            )

            split_documents = text_splitter.split_documents([document])

            self.db.add_documents(split_documents)

    def create_embedding(self, text: str, embedding_model="text-embedding-ada-002"):
        return openai.Embedding.create(input=[text], model=embedding_model)["data"][0][
            "embedding"
        ]

    def review_chunk(self, chunk: str):
        result = self.chain(
            inputs={
                "input": input,
                "system_prompt": self.llm_arguments_configuration.system_prompt,
            }
        )

    def get_openai_api_key():
        return dotenv_values().get("OPENAI_API_KEY")
