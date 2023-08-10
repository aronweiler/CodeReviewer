import logging
import os
from typing import List
from github import Github
from github import Auth

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from integrations.commenter_base import CommenterBase, CodeComment


class GitHubCommenter(CommenterBase):
    def __init__(self):
        # using an access token
        # Get the GITHUB_TOKEN from the environment
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.auth = Auth.Token(self.github_token)

        # Public Web Github
        self.github = Github(auth=self.auth)

        # Example of using an access token with a GitHub Enterprise Base URL
        # Github Enterprise with custom hostname
        # g = Github(base_url="https://{hostname}/api/v3", auth=auth)

    def add_comments(self, comments: List[CodeComment]):
        github_output = os.environ.get("GITHUB_OUTPUT", None)
        logging.debug("GH Output: " + github_output)

        # Get the pull request number from the environment
        github_repo = os.environ.get("GITHUB_REPOSITORY")
        github_ref = os.environ.get("GITHUB_REF")
        github_pr = os.environ.get("GITHUB_PR")

        pr = self.github.get_repo(github_repo).get_pull(int(github_pr))

        # TODO: Get this working!

        for comment in comments:
            # Create a comment on a pull request
            # https://docs.github.com/en/rest/reference/pulls#create-a-review-for-a-pull-request

            pr.create_review(                
                body=comment.comment_in_markdown,
                event="COMMENT",
                comments=[
                    {
                        "path": comment.file_path,
                        "start_line": comment.starting_line_number,
                        "line": comment.ending_line_number,
                        "body": comment.comment_in_markdown,
                        "side": "RIGHT"
                    }
                ],
            )

        # Write the output to the $GITHUB_OUTPUT environment file
        # See: https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action?learn=create_actions&learnProduct=actions#writing-the-action-code
        # Eventually this summary should be output as markdown and then added to the PR
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"review_summary={summary}")


# Testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    commenter = GitHubCommenter()
    commenter.add_comments(
        [
            CodeComment(
                starting_line_number=1,
                ending_line_number=1,
                comment_in_markdown="This is a test comment",
                file_path="src/llms/memory/postgres_entity_store.py",
            )
        ]
    )