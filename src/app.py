import os
import logging
import sys
import argparse

from integrations.github_commenter import GitHubCommenter
from code_reviewer import CodeReviewer
from review_configuration import ReviewConfiguration

PROVIDERS = {"github": GitHubCommenter(), "gitlab": None, "bitbucket": None}


class ReviewRunner:
    def __init__(self):
        self.parse_arguments()
        #self.set_logging_level()

    def parse_arguments(self):
        # Add arguments
        parser = argparse.ArgumentParser()
        
        parser.add_argument("file_paths", nargs="+", help="List of file paths.")

        self.args = parser.parse_args()

    def set_logging_level(self):
        # Set the logging level
        numeric_level = getattr(logging, self.args.logging_level.upper(), None)
        logging.basicConfig(level=numeric_level)
        logging.info("Started logging")

    def main(self):
        # Get the paths to the source code files
        paths = self.args.file_paths
        logging.debug("Paths: " + str(paths))

        configuration = ReviewConfiguration.from_environment()

        # Get the source code files
        source_code_files = []
        for path in paths:
            if os.path.isfile(path):
                source_code_files.append(path)
            else:
                logging.warning(f"Path does not exist: {path}")

        logging.debug("Source code files: " + str(source_code_files))

        # Run the code review
        code_comments = self.do_review(source_code_files, configuration)

        # Have the provider-specific code add the review to the PR
        PROVIDERS[configuration.provider].add_comments(code_comments)


    def do_review(self, source_code_files, configuration: ReviewConfiguration):        
        code_reviewer = CodeReviewer(configuration)
        review = code_reviewer.review(source_code_files)
        return review


if __name__ == "__main__":
    ReviewRunner().main()
