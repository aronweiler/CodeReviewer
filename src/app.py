import os
import logging
from typing import List

from review.code_reviewer import CodeReviewer
from refactor.code_refactor import CodeRefactor
from code_reviewer_configuration import CodeReviewerConfiguration
from code_reviewer_configuration import PROVIDERS

VALID_TYPES = ["review", "refactor", "document"]


class ReviewRunner:
    def __init__(self):
        self.load_arguments()
        self.set_logging_level()
        self.configuration = CodeReviewerConfiguration.from_environment()

    def main(self):
        # Lowercase the type to ensure case-insensitive comparison
        operation_type = self.cr_type.lower()
        if operation_type == "review":
            self.do_code_review()
        elif operation_type == "refactor":
            self.do_code_refactor()
        elif operation_type == "document":
            self.do_code_documentation()
        else:
            raise ValueError(f"Invalid type: {self.cr_type}")

    def do_code_refactor(self):
        # Get the source code files
        source_code_files = self.get_source_code_files()

        # Get the source and target branches from arguments
        source_branch = self.source_branch
        target_branch = self.target_branch

        # Initialize the CodeRefactor class and run the refactor
        code_refactor = CodeRefactor(self.configuration)
        refactored_code_documents = code_refactor.refactor(source_code_files)

        # Get the provider from the configuration and perform provider-specific operations
        provider = PROVIDERS[self.configuration.provider.lower()]
        provider.commit_changes(
            source_branch=source_branch,
            target_branch=target_branch,
            commit_message="Auto-Refactor",
            metadatas=refactored_code_documents,
        )

    def do_code_documentation(self):
        # Documentation functionality to be implemented
        pass

    def do_code_review(self):
        # Get the source code files
        source_code_files = self.get_source_code_files()

        # Initialize the CodeReviewer class and run the review
        code_reviewer = CodeReviewer(self.configuration)
        review = code_reviewer.review(source_code_files)

        # Get the provider from the configuration and add the review comments to the PR
        provider = PROVIDERS[self.configuration.provider.lower()]
        provider.add_pr_comments(review)

    def get_source_code_files(self) -> List[str]:
        # Get the paths to the source code files from arguments
        paths = self.target_files
        if paths is None or len(paths) == 0:
            logging.info("No paths specified, using all files in repo")

        logging.debug("Code Refactor Paths: " + str(paths))

        # Check if each path is a file and add it to the source code files list
        source_code_files = [path for path in paths if os.path.isfile(path)]
        source_code_directories = [path for path in paths if os.path.isdir(path)]
        
        # If a directory is specified, add all files in the directory to the source code files list
        for directory in source_code_directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    source_code_files.append(os.path.join(root, file))

        logging.debug("Source code files: " + str(source_code_files))

        return source_code_files

    def load_arguments(self):
        # Load the arguments from the environment

        # These are set in the LLMConfiguration class
        # self.model = os.getenv("CR_MODEL", "gpt-3.5-turbo-0613")
        # self.temperature = os.getenv("CR_TEMPERATURE", "0.0")
        # self.max_supported_tokens = os.getenv("CR_MAX_SUPPORTED_TOKENS", "4096")
        # self.max_completion_tokens = os.getenv("CR_MAX_COMPLETION_TOKENS", "2048")

        self.log_level = os.getenv("CR_LOG_LEVEL", "info")
        self.source_branch = os.getenv("CR_SOURCE_BRANCH", "main")
        self.target_branch = os.getenv("CR_TARGET_BRANCH", "test-branch")
        self.cr_type = os.getenv("CR_TYPE", None)
        self.target_files = os.getenv("CR_TARGET_FILES", "")

        # Split the target files string into a list
        self.target_files = self.target_files.split(",")
        logging.debug("Target files: " + str(self.target_files))

        # Validate that the type argument is one of the valid choices
        if self.cr_type.lower() not in VALID_TYPES:
            raise ValueError(
                f"Invalid type: {self.cr_type}. Valid types are: {VALID_TYPES}"
            )

    def set_logging_level(self):
        # Get the numeric value of the logging level and set it
        numeric_level = getattr(logging, self.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.log_level}")
        logging.basicConfig(level=numeric_level)
        logging.info("Started logging")


if __name__ == "__main__":
    ReviewRunner().main()
