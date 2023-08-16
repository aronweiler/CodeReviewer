import os
import logging
from typing import List

from review.code_reviewer import CodeReviewer
from refactor.code_refactor import CodeRefactor
from document.document_code import DocumentCode
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

        if len(source_code_files) == 0:
            raise ValueError("No source code files found")

        # Get the source and target branches from arguments
        source_branch = self.source_branch
        target_branch = self.target_branch

        # Initialize the CodeRefactor class and run the refactor
        code_refactor = CodeRefactor(self.configuration)
        refactored_code_documents = code_refactor.refactor(source_code_files)

        # Get the provider from the configuration and perform provider-specific operations
        provider = PROVIDERS[self.configuration.provider.lower()]()
        provider.commit_changes(
            source_branch=source_branch,
            target_branch=target_branch,
            commit_message="Auto-Refactor",
            metadatas=refactored_code_documents,
        )

    def do_code_documentation(self):
        # Documentation functionality to be implemented
        source_code_files = self.get_source_code_files()

        if len(source_code_files) == 0:
            raise ValueError("No source code files found")
        
        # Code documentation requires a template or input file to be specified
        if self.document_template is None:
            raise ValueError("No document template specified")
        
        if self.document_output is None:
            raise ValueError("No document output specified")
        
        code_documenter = DocumentCode(self.configuration)

        documentation = code_documenter.document(source_code_files, self.document_template, self.update_existing_documentation)

        # Write the documentation to the output file
        with open(self.document_output, "w") as f:
            f.write(documentation)

    def do_code_review(self):
        # Get the source code files
        source_code_files = self.get_source_code_files()

        if len(source_code_files) == 0:
            raise ValueError("No source code files found")

        # Initialize the CodeReviewer class and run the review
        code_reviewer = CodeReviewer(self.configuration)
        review = code_reviewer.review(source_code_files)

        # Get the provider from the configuration and add the review comments to the PR
        provider = PROVIDERS[self.configuration.provider.lower()]()
        provider.add_pr_comments(review)

    def get_source_code_files(self) -> List[str]:
        # Get the paths to the source code files from arguments
        paths = self.target_files
        if paths is None or len(paths) == 0:
            logging.info("No paths specified, using all files in repo")
            paths = [os.getcwd()]

        logging.debug("Code Refactor Paths: " + str(paths))

        # Function to recursively get all files within a directory, excluding hidden and specified directories
        def get_files_recursively(directory):
            files = []
            for root, dirs, filenames in os.walk(directory):
                # Exclude hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                # Exclude specified directories
                dirs[:] = [d for d in dirs if d not in self.exclude_directories]
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return files

        source_code_files = []

        for path in paths:
            if os.path.isfile(path):
                source_code_files.append(path)
            elif os.path.isdir(path):
                source_code_files.extend(get_files_recursively(path))
            else:
                logging.warning(f"Invalid path: {path}")

        logging.debug("Source code files: " + str(source_code_files))

        return source_code_files

    def load_arguments(self):
        # Load the arguments from the environment
        # Model, temp, and tokens are set in the LLMConfiguration class

        self.log_level = os.getenv("CR_LOG_LEVEL", "info")
        self.source_branch = os.getenv("CR_SOURCE_BRANCH", "main")
        self.target_branch = os.getenv("CR_TARGET_BRANCH", "test-branch")
        self.cr_type = os.getenv("CR_TYPE", None)
        self.target_files = os.getenv("CR_TARGET_FILES", None)
        
        # Documentation arguments
        self.update_existing_documentation = os.getenv("CR_UPDATE_EXISTING_DOCUMENTATION", "false").lower() == "true"
        self.document_template = os.getenv("CR_DOCUMENT_TEMPLATE", None)
        self.document_output = os.getenv("CR_DOCUMENT_OUTPUT", None)

        # Get any directories to exclude from the target files
        self.exclude_directories = os.getenv("CR_EXCLUDE_DIRECTORIES", None)

        # Split the target files string into a list
        if self.target_files is not None:
            self.target_files = self.target_files.split(",")
            logging.debug("Target files: " + str(self.target_files))

        # Split the target files string into a list
        if self.exclude_directories is not None:
            self.exclude_directories = self.exclude_directories.split(",")
            logging.debug("Excluded directories: " + str(self.exclude_directories))

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
        logging.root.setLevel(level=numeric_level)
        logging.info("Started logging")


if __name__ == "__main__":
    ReviewRunner().main()
