import logging
import os
import sys
from typing import List
from github import Github, Auth, InputGitTreeElement

# Append the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from integrations.source_control_base import SourceControlBase, CodeComment

REGULAR_FILE = "100644"


class GitHubIntegration(SourceControlBase):
    def __init__(self):
        # Get the GITHUB_TOKEN from the environment
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN is not set in the environment")

        # Authenticate with Github using the token
        self.auth = Auth.Token(self.github_token)
        self.github = Github(auth=self.auth)

    def commit_changes(
        self, source_branch, target_branch, commit_message, metadatas: List[dict]
    ):
        repository = os.getenv("GITHUB_REPOSITORY")
        if not repository:
            raise ValueError("GITHUB_REPOSITORY is not set in the environment")

        repo = self.github.get_repo(repository)

        # This call ensures the branch is created
        commit_branch = self._create_branch(repository, source_branch, target_branch)

        # Get the base tree
        base_tree = repo.get_git_tree(sha=source_branch)

        # Create a new tree with the changes
        tree_elements = []
        for metadata in metadatas:
            path = metadata["file_path"]
            code = metadata["code"]
            # Does the encoding need to match the source?  Probably should find out and adjust this if necessary.
            blob = repo.create_git_blob(content=code, encoding="utf-8")
            git_tree_element = InputGitTreeElement(
                path=path, mode=REGULAR_FILE, type="blob", sha=blob.sha
            )
            tree_elements.append(git_tree_element)

        new_tree = repo.create_git_tree(tree_elements, base_tree)

        # Create the commit
        new_commit = repo.create_git_commit(
            message=commit_message,
            tree=repo.get_git_tree(sha=new_tree.sha),
            parents=[repo.get_git_commit(repo.get_branch(source_branch).commit.sha)],
        )

        # Push the commit to the new branch by editing the reference
        # branch_ref = repo.get_git_ref(ref=f"heads/{target_branch}")
        print(f"{target_branch}_ref: {commit_branch}")

        # Give it a good shove
        commit_branch.edit(sha=new_commit.sha, force=True)

        logging.info("Changes committed and pushed successfully!")

    def _create_branch(self, repository, source_branch, target_branch):
        repo = self.github.get_repo(repository)

        # Get the latest commit of the source branch
        source_ref = repo.get_git_ref(f"heads/{source_branch}")
        commit_sha = source_ref.object.sha

        # See if the target branch already exists
        try:
            branch = repo.get_git_ref(f"heads/{target_branch}")
            logging.info(f"Branch '{target_branch}' already exists!")
            return branch
        except:
            pass

        # Create the new branch with the specified commit
        new_branch = repo.create_git_ref(f"refs/heads/{target_branch}", commit_sha)
        logging.info(f"New branch '{target_branch}' created successfully!")
        return new_branch

    def add_pr_comments(self, comments: List[CodeComment]):
        github_output = os.getenv("GITHUB_OUTPUT", None)
        logging.debug("GH Output: " + github_output)

        github_repo = os.getenv("GITHUB_REPOSITORY")
        github_pr = os.getenv("GITHUB_PR")

        if not github_repo or not github_pr:
            raise ValueError(
                "GITHUB_REPOSITORY or GITHUB_PR is not set in the environment"
            )

        pr = self.github.get_repo(github_repo).get_pull(int(github_pr))

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
                        "side": "RIGHT",
                    }
                ],
            )

        # Write the output to the $GITHUB_OUTPUT environment file
        # See: https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action?learn=create_actions&learnProduct=actions#writing-the-action-code
        # Eventually this summary should be output as markdown and then added to the PR
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"review_summary={summary}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    github_integration = GitHubIntegration()

    github_integration.commit_changes(
        source_branch="main",
        target_branch="test-branch",
        commit_message="Test commit",
        code_documents=[
            {
                "file_path": "examples/code_comment.py",
                "code": "def test():\n    print('hello world')\n",
            }
        ],
    )

    # commenter.add_pr_comments(
    #     [
    #         CodeComment(
    #             starting_line_number=1,
    #             ending_line_number=1,
    #             comment_in_markdown="This is a test comment",
    #             file_path="src/llms/memory/postgres_entity_store.py",
    #         )
    #     ]
    # )
