import json
import re
from uuid import uuid4
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
    DIFF_REVIEW_TEMPLATE,
    CONTEXT_EXTRACTION_PROMPT,
    CONTEXT_EXTRACTION_TEMPLATE,
)
from utilities.token_helper import simple_get_tokens_for_message
from review.code_comment import CodeComment
from review.vector_database_search_chain import VectorDatabaseSearchChain
from integrations.diff import Diff
from utilities.open_ai import get_openai_api_key

from language_support.python import PythonExtractor

# TODO: Expand this list- most of the stuff we have doesn't need to be split, anyway.
SUPPORTED_FILE_TYPES = {    
    "py": Language.PYTHON,
    "cpp": Language.CPP,
    "md": Language.MARKDOWN,
}

SUPPORTED_EXTRACTOR_TYPES = {
    "py": PythonExtractor,
}


class DiffReviewer:
    def __init__(self, configuration: CodeReviewerConfiguration):
        self.configuration = configuration
        self.llm_arguments_configuration = configuration.llm_arguments

        self.llm = ChatOpenAI(
            model=self.llm_arguments_configuration.model,
            temperature=self.llm_arguments_configuration.temperature,
            openai_api_key=get_openai_api_key(),
            max_tokens=self.llm_arguments_configuration.max_completion_tokens,
        )

        self.extract_chain = LLMChain(llm=self.llm, prompt=CONTEXT_EXTRACTION_PROMPT)
        self.review_chain = LLMChain(llm=self.llm, prompt=DIFF_REVIEW_PROMPT)

    def get_remaining_prompt_tokens(self, prompt_template):
        return (
            self.llm_arguments_configuration.max_supported_tokens
            - self.llm_arguments_configuration.max_completion_tokens
            - simple_get_tokens_for_message(prompt_template)
        )

    def review(
        self,
        diffs: List[Diff],
        files_to_include_as_context: List[str],
        include_deleted_files=False,
    ) -> List[CodeComment]:
        # TODO: Should load all of the documents in the repository into the data store for reference by the LLM reviewing the diff
        vector_db = self.split_and_add_to_datastore(files_to_include_as_context)

        # retriever = vector_db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5})
        # vector_db_chain = VectorDatabaseSearchChain(self.configuration, vector_db)

        for diff in diffs:
            if diff.new_file:
                # Treat this differently if it's a brand new file
                # TODO: Review the whole file using the code_reviewer.py
                continue
            if not diff.deleted_file or include_deleted_files:
                remaining_prompt_tokens = self.get_remaining_prompt_tokens(CONTEXT_EXTRACTION_TEMPLATE.format(diff=diff.diff_content))
                # If the diff is too big, split that first                
                if remaining_prompt_tokens <= 1:
                    split_diffs = self.split_diff(diff.diff_content)
                else:
                    split_diffs = [diff.diff_content]

                context_to_lookup = []
                for split in split_diffs:
                    # Extract things to look for in loaded context files
                    context_lookup_json = self.extract_chain.run({"diff": split}).split(
                        "\n"
                    )
                    
                    for json_data in context_lookup_json:
                        if json_data.strip() != "":
                            context_to_lookup.append(
                                ContextLookup(**json.loads(json_data))
                            )

                    # Lookup the context data
                    relevant_context:Dict[str, List[str]] = {}
                    already_included = []
                    for context in context_to_lookup:                    
                        results = (
                            vector_db.similarity_search_by_vector_with_relevance_scores(
                                self.create_embedding(
                                    context.reference_type + " : " + context.missing_context
                                ),
                                k=10, # Only geting the top 10 results right now
                            )
                        )
                        # TODO: Use extracted metadata when it's available. (Currently it's only doing a similarity search) 
                        # Extract the type of reference from the initial context lookup, and then use it to filter on metadata.
                        # vector_db.similarity_search_with_relevance_scores("CodeComment", search_kwargs={"filter":{"classes":"CodeComment"}})
                        # More example search kwargs:
                        # search_kwargs={"filter":{'$or': [{'source': {'$eq': './SampleDoc/Bikes.pdf'}}, {'source': {'$eq': './SampleDoc/IceCreams.pdf'}}]}}
                        for content, score in results:
                            print(f"Relevance score: {score}.  File: {content.metadata['file_name']}")
                            
                            if content.metadata["id"] in already_included:
                                continue
                            
                            already_included.append(content.metadata["id"])
                            
                            if "imports" in content.metadata:
                                relevant_context["imports"] = list(set(relevant_context.get("imports", []) + content.metadata["imports"].split(',')))

                            if "classes" in content.metadata:
                                relevant_context["available classes"] = list(set(relevant_context.get("available classes", []) + content.metadata["classes"].split(',')))

                            if "functions" in content.metadata:
                                relevant_context["available functions"] = list(set(relevant_context.get("available functions", []) + content.metadata["functions"].split(',')))

                   
                            
                            # (
                            #     f"\n--------{content.metadata['file_name']}---------\n"
                            #     + content.page_content
                            #     + "\n-----------------\n"
                            # )

                    imports_str = ", ".join(relevant_context.get("imports", []))
                    classes_str = ", ".join(relevant_context.get("available classes", []))
                    functions_str = ", ".join(relevant_context.get("available functions", []))


                    # Create the formatted string
                    relevant_context_str = f"Imports: {imports_str}\nAvailable Classes: {classes_str}\nAvailable Functions: {functions_str}"


                    # Review the chunk
                    diff_review = self.review_chain.run(diff=split, context=relevant_context_str)
                    comments = self.get_comments(diff_review)

                diff.review_comments = comments

        return diffs

    def create_embedding(self, text: str, embedding_model="text-embedding-ada-002"):
        return openai.Embedding.create(input=[text], model=embedding_model)["data"][0][
            "embedding"
        ]

    def split_diff(self, diff):
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n=@@", "\n "],
            is_separator_regex=True,
            chunk_size = 100,
            chunk_overlap  = 0,
            length_function = simple_get_tokens_for_message
            )

        splits = splitter.split_text(diff)

        return splits

    def get_comments(self, diff_review: str) -> List[CodeComment]:
        diff_review_json = json.loads(diff_review)
        comments = []
        for comment in diff_review_json["comments"]:
            comments.append(CodeComment(**comment, file_path=file_path))

        return comments

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
                chunk_size=50, # Super small document sizes for lookup and context injection
                chunk_overlap=0,
                keep_separator=True,
                length_function=simple_get_tokens_for_message,
            )

            # Unwind this dumbass list-in-a-list
            joined_docs = code_splitter.create_documents([file_contents])
            
            # Get some extracted data
            metadata = {}
            if file_extension in SUPPORTED_EXTRACTOR_TYPES:
                metadata = SUPPORTED_EXTRACTOR_TYPES[file_extension].extract_metadata(file_contents)

            # Add metadata to all of these
            for d in joined_docs:
                d.metadata = metadata
                d.metadata["id"] = str(uuid4()) # for use when comparing chunks later
                d.metadata["file_name"] = file

            [documents.append(d) for d in joined_docs]

        return Chroma.from_documents(
            documents, OpenAIEmbeddings(openai_api_key=get_openai_api_key())
        )



class ContextLookup:
    def __init__(self, missing_context, reference_type, reason):
        self.missing_context = missing_context
        self.reason = reason
        self.reference_type = reference_type


# Testing
if __name__ == "__main__":
    pass
