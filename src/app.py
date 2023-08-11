import os
import logging
import argparse
from typing import List

from review.code_reviewer import CodeReviewer
from refactor.code_refactor import CodeRefactor
from code_reviewer_configuration import CodeReviewerConfiguration
from code_reviewer_configuration import PROVIDERS

VALID_TYPES = ["review", "refactor", "document"]


class ReviewRunner:
    def __init__(self):
        self.parse_arguments()
        self.set_logging_level()
        self.configuration = CodeReviewerConfiguration.from_environment()

    def main(self):
        # Lowercase the type to ensure case-insensitive comparison
        operation_type = self.args.type.lower()
        if operation_type == "review":
            self.do_code_review()
        elif operation_type == "refactor":
            self.do_code_refactor()
        elif operation_type == "document":
            self.do_code_documentation()

    def do_code_refactor(self):
        # Get the source code files
        source_code_files = self.get_source_code_files()

        # Get the source and target branches from arguments
        source_branch = self.args.source_branch
        target_branch = self.args.target_branch

        # Initialize the CodeRefactor class and run the refactor
        code_refactor = CodeRefactor(self.configuration)
        refactored_code_documents = code_refactor.refactor(source_code_files)

        # Get the provider from the configuration and perform provider-specific operations
        provider = PROVIDERS[self.configuration.provider.lower()]
        provider.commit_changes(
            source_branch=source_branch,
            target_branch=target_branch,
            commit_message="Auto-Refactor",
            metadatas=refactored_code_documents['metadatas'],
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
        paths = self.args.file_paths
        logging.debug("Code Refactor Paths: " + str(paths))

        # Check if each path is a file and add it to the source code files list
        source_code_files = [path for path in paths if os.path.isfile(path)]
        for path in paths:
            if not os.path.isfile(path):
                logging.warning(f"Path does not exist: {path}")

        logging.debug("Source code files: " + str(source_code_files))

        return source_code_files

    def parse_arguments(self):
        # Initialize the argument parser and add arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--logging-level", default="INFO", help="Logging level. Default: INFO"
        )
        parser.add_argument(
            "--type",
            required=True,
            help=f"Type of run. Choices are: {str(VALID_TYPES)}",
        )
        parser.add_argument(
            "--source_branch",
            default="main",
            help="Source branch to pull from. Default: main",
        )
        parser.add_argument(
            "--target_branch",
            default="code-refactor",
            help="Target branch to push to. Default: code-refactor",
        )
        parser.add_argument("file_paths", nargs="+", help="List of file paths.")

        self.args = parser.parse_args()

        # Validate that the type argument is one of the valid choices
        if self.args.type.lower() not in VALID_TYPES:
            raise ValueError(
                f"Invalid type: {self.args.type}. Valid types are: {VALID_TYPES}"
            )

    def set_logging_level(self):
        # Get the numeric value of the logging level and set it
        numeric_level = getattr(logging, self.args.logging_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.args.logging_level}")
        logging.basicConfig(level=numeric_level)
        logging.info("Started logging")


if __name__ == "__main__":
    ReviewRunner().main()
