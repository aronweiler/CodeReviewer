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
from review.vector_database_search_chain import VectorDatabaseSearchChain
from integrations.diff import Diff
from utilities.open_ai import get_openai_api_key

# TODO: Expand this list- most of the stuff we have doesn't need to be split, anyway.
SUPPORTED_FILE_TYPES = {"py": Language.PYTHON, "cpp": Language.CPP, "md": Language.MARKDOWN}


class DiffReviewer:
    def __init__(self, configuration: CodeReviewerConfiguration):
        self.configuration = configuration
        self.llm_arguments_configuration = configuration.llm_arguments

        self.remaining_prompt_tokens = (
            self.llm_arguments_configuration.max_supported_tokens
            - self.llm_arguments_configuration.max_completion_tokens
            - simple_get_tokens_for_message(DIFF_REVIEW_TEMPLATE)
        )

        self.llm = ChatOpenAI(
            model=self.llm_arguments_configuration.model,
            temperature=self.llm_arguments_configuration.temperature,
            openai_api_key=get_openai_api_key(),
            max_tokens=self.llm_arguments_configuration.max_completion_tokens,
        )

        self.review_chain = LLMChain(llm=self.llm, prompt=DIFF_REVIEW_PROMPT)        

    def review(self, diffs: List[Diff], files_to_include_as_context:List[str]) -> List[CodeComment]:
        # TODO: Should load all of the documents in the repository into the data store for reference by the LLM reviewing the diff
        vector_db = self.split_and_add_to_datastore(files_to_include_as_context)

        vector_db_chain = VectorDatabaseSearchChain(self.configuration, vector_db)
                
        for diff in diffs:            
            # Review the chunk
            diff_review = vector_db_chain.run(f"Use the search and lookup tools to find and return all of the relevant context related to this diff:\n\n{diff.diff_content}")
            comments = self.get_comments(diff_review)
            
            diff.review_comments = comments

        return diffs

    def get_comments(self, diff_review: str) -> List[CodeComment]:
        diff_review_json = json.loads(diff_review)
        comments = []
        for comment in diff_review_json["comments"]:
            comments.append(CodeComment(**comment, file_path=file_path))

        return comments
    

    def review_diff(self, diff: str) -> str:
        return self.review_chain()
    

    def split_and_add_to_datastore(self, target_files) -> Chroma:
        # Split the file into chunks of (max_tokens - max_completion_tokens)
        # This is because the LLM will need to add the completion tokens to the end of the chunk
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
            logging.debug(f"Language is {language} for {file}")

            # Read the file in
            with open(file, "r") as f:
                file_contents = f.read()

            # TODO: When looking at diffs for review, I need to diff two versions of this file,
            # and then extract the chunks of diffs (much like git does),
            # then need to ingest that into the datastore along with the full file
            code_splitter = RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=self.remaining_prompt_tokens,
                chunk_overlap=0,
                keep_separator=True,
                add_start_index=True,
                length_function=simple_get_tokens_for_message,
            )

            # Unwind this dumbass list-in-a-list
            joined_docs = code_splitter.create_documents([file_contents])
            docs = [d for d in joined_docs]

            all_lines = file_contents.rstrip().split("\n")

            # Create a list of docs with the medadata
            chunk = 0
            starting_search_line_index = 0
            for d in docs:
                chunk += 1
                # Find the true starting line number
                for line_number, line in enumerate(
                    all_lines[starting_search_line_index:], start=1
                ):
                    if d.page_content.split("\n")[0] in line:
                        starting_line = line_number + starting_search_line_index
                        starting_search_line_index = line_number + 1
                        break

                d.metadata = {
                    "file_path": file,
                    "chunk": chunk,
                    "language": language,
                    "starting_line_number": starting_line,
                }

                # Because of how little LLMs pay attention to things like a single line number prompt,
                # (e.g. ----- BEGIN CODE: Starting Line #: {starting_line_number}  -----)
                # I am going to add line numbers to each line of code
                page_content_lines = d.page_content.split("\n")
                for i, line in enumerate(page_content_lines, start=0):
                    page_content_lines[i] = f"{i + starting_line}: {line}"

                d.page_content = "\n".join(page_content_lines)

                documents.append(d)

            logging.debug(f"Split {file} into {chunk} chunks")

        return Chroma.from_documents(documents, OpenAIEmbeddings(openai_api_key=get_openai_api_key()))

# Testing
if __name__ == "__main__":
    pass