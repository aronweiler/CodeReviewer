import os
import logging
import argparse
from typing import List

from review.code_reviewer import CodeReviewer
from code_reviewer_configuration import CodeReviewerConfiguration
from code_reviewer_configuration import PROVIDERS


class ReviewRunner:
    def __init__(self):
        self.parse_arguments()
        self.set_logging_level()

        self.configuration = CodeReviewerConfiguration.from_environment()

    def main(self):
        if self.args.type == "review":
            self.do_code_review()
        elif self.args.type == "refactor":
            self.do_code_refactor()     
        
    def do_code_refactor(self):
        # Run the refactor
        source_code_files = self.get_source_code_files()

        source_branch = self.args.source_branch
        target_branch = self.args.target_branch        

        code_refactor = CodeRefactor(self.configuration, source_branch, target_branch)
        refactored_code = code_refactor.refactor(source_code_files)
        
        # Have the provider-specific code create the refactor branch with the results
        provider = PROVIDERS[self.configuration.provider.lower()]
        provider.create_refactor_branch(source_branch, target_branch, refactored_code)

    def do_code_review(self):
        # Run the code review
        source_code_files = self.get_source_code_files()

        code_reviewer = CodeReviewer(self.configuration)
        review = code_reviewer.review(source_code_files)
        
        # Have the provider-specific code add the comments to the PR
        provider = PROVIDERS[self.configuration.provider.lower()]
        provider.add_pr_comments(review)

    def get_source_code_files(self) -> List[str]:
        # Get the paths to the source code files
        paths = self.args.file_paths
        logging.debug("Code Refactor Paths: " + str(paths))        

        # Get the source code files
        source_code_files = []
        for path in paths:
            if os.path.isfile(path):
                source_code_files.append(path)
            else:
                logging.warning(f"Path does not exist: {path}")

        logging.debug("Source code files: " + str(source_code_files))

        return source_code_files

    def parse_arguments(self):
        # Add arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--logging-level",
            default="INFO",
            help="Logging level. Default: INFO",
        )

        parser.add_argument(
            "--type",
            default="review",
            help="Type of run. Default: review",
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

    def set_logging_level(self):
        # Set the logging level
        numeric_level = getattr(logging, self.args.logging_level.upper(), None)
        logging.basicConfig(level=numeric_level)
        logging.info("Started logging")


if __name__ == "__main__":
    ReviewRunner().main()
