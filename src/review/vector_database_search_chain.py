import json
from enum import Enum
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import openai
from dotenv import dotenv_values
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
import logging
from datetime import datetime
from typing import Union, List, Dict
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from code_reviewer_configuration import CodeReviewerConfiguration
from review.prompts import (
    DIFF_REVIEW_PROMPT,
    DIFF_REVIEW_TEMPLATE
)
from utilities.token_helper import simple_get_tokens_for_message
from review.code_comment import CodeComment
from integrations.diff import Diff
from utilities.open_ai import get_openai_api_key
from langchain import OpenAI, Wikipedia
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.agents.react.base import DocstoreExplorer
from langchain.docstore.base import Docstore

class VectorDatabaseSearchChain:
    def __init__(self, configuration: CodeReviewerConfiguration, memory_vector_db:Chroma):
        self.configuration = configuration
        self.llm_arguments_configuration = configuration.llm_arguments
        
        self.memory_vector_db = memory_vector_db
        self.docstore = DocstoreExplorer(CodeDocstore(memory_vector_db))
        
        tools = [
            Tool(
                name="Search",
                func=self.docstore.search,
                description="useful for when you need to ask with search",
            ),
            Tool(
                name="Lookup",
                func=self.docstore.lookup,
                description="useful for when you need to ask with lookup",
            ),
        ]
        
        self.llm = ChatOpenAI(
            model=self.llm_arguments_configuration.model,
            temperature=self.llm_arguments_configuration.temperature,
            openai_api_key=get_openai_api_key(),
            max_tokens=self.llm_arguments_configuration.max_completion_tokens,
        )

        self.react = initialize_agent(tools, self.llm, agent=AgentType.REACT_DOCSTORE, verbose=True)
        
    def run(self, question) -> str:
        output = self.react.run(question)
        
        return output
        
        
class CodeDocstore(Docstore):
    def __init__(self, vector_database:Chroma) -> None:
        super().__init__()
        
        self.vector_database = vector_database
        
    def search(self, search: str) -> Union[str, Document]:
        # Create the embedding for the search string
        # query_embedding = self.create_embedding(search)
        
        # TODO: Make search parameters configurable and tune them. 
        # Only retrieve the top-most likely document
        retriever = self.vector_database.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .6, "k": 1})
        
        # Investigate using metadata here, as well
        documents = retriever.get_relevant_documents(search)
        
        return "Code document", documents[0]
        
    # def create_embedding(self, text: str, embedding_model="text-embedding-ada-002"):
    #     return openai.Embedding.create(input=[text], model=embedding_model)["data"][0][
    #         "embedding"
    #     ]
        
        