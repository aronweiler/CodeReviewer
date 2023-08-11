import logging
import os
from typing import List
from github import Github, Auth

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from integrations.source_control_base import SourceControlBase, CodeComment


class GitHubIntegration(SourceControlBase):
    def __init__(self):
        # using an access token
        # Get the GITHUB_TOKEN from the environment
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.auth = Auth.Token(self.github_token)

        # Public Web Github
        self.github = Github(auth=self.auth)

    def commit_changes(self, branch_name, commit_message, code_documents):
        repository = os.environ.get("GITHUB_REPOSITORY")
        repo = self.github.get_repo(repository)
        branch = repo.get_branch(branch_name)
        
        # Get the latest commit of the branch
        latest_commit = repo.get_commit(branch.commit.sha)
        
        # Create a new tree with the changes
        new_tree = []
        for doc in code_documents:
            code = doc['metadatas']['refactored_code']                
            blob = repo.create_git_blob(code, 'base64')
            # What??
            #new_tree.append(repo.create_git_tree(doc['metadatas']['file_path'], blob.sha, '100644'))

        new_tree_sha = repo.create_git_tree(new_tree).sha
        
        # Create a new commit
        new_commit = repo.create_git_commit(commit_message, new_tree_sha, [latest_commit.sha])
        
        # Update the branch reference to point to the new commit
        branch.edit(commit=new_commit.sha)

        logging.info("Changes committed and pushed successfully!")


    def create_branch(self, source_branch, target_branch):
        repository = os.environ.get("GITHUB_REPOSITORY")
        repo = self.github.get_repo(repository)

        # Get the latest commit of the source branch
        source_ref = repo.get_git_ref(f"heads/{source_branch}")
        commit_sha = source_ref.object.sha

        # Create the new branch with the specified commit
        repo.create_git_ref(f"refs/heads/{target_branch}", commit_sha)

        logging.info(f"New branch '{target_branch}' created successfully!")

    def add_pr_comments(self, comments: List[CodeComment]):
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