import logging
import os
import sys
from typing import List

import gitlab

# Append the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from integrations.source_control_base import SourceControlBase, CodeComment

class GitLabIntegration(SourceControlBase):
    def __init__(self):
        # Get the GITLAB_TOKEN from the environment
        self.gitlab_token = os.getenv("GITLAB_TOKEN")
        if not self.gitlab_token:
            raise ValueError("GITLAB_TOKEN is not set in the environment")
        
        self.gitlab_url = os.getenv("GITLAB_URL")
        if not self.gitlab_url:
            raise ValueError("GITLAB_URL is not set in the environment")

        # private token or personal token authentication (self-hosted GitLab instance)
        self.gl = gitlab.Gitlab(url=self.gitlab_url, private_token=self.gitlab_token)

        # make an API request to create the gl.user object. This is not required but may be useful
        # to validate your token authentication. Note that this will not work with job tokens.
        self.gl.auth()

        # Enable "debug" mode. This can be useful when trying to determine what
        # information is being sent back and forth to the GitLab server.
        # Note: this will cause credentials and other potentially sensitive
        # information to be printed to the terminal.
        #self.gl.enable_debug()


    def add_pr_comments(self, comments: List[CodeComment]):
        """Adds comments to the target PR/MR

        Args:
            comments (List[CodeComment]): list of code comments to add
        """
        project_id = os.getenv("CI_PROJECT_ID")
        if not project_id:
            raise ValueError("CI_PROJECT_ID is not set in the environment")
        
        merge_request_id = os.getenv("CI_MERGE_REQUEST_ID")
        if not merge_request_id:
            raise ValueError("CI_MERGE_REQUEST_ID is not set in the environment")
        
        project = self.gl.projects.get(project_id)
        merge_request = project.mergerequests.get(merge_request_id)
    
    def add_commit_comments(self, comments: List[CodeComment]):
        """Adds comments to the latest commit on the CR_SOURCE_BRANCH.  Note: This does not add multi-line comments, and does not work on anything that isn't within the diff (lame).

        Args:
            comments (List[CodeComment]): list of code comments to add
        """
        project_id = os.getenv("CI_PROJECT_ID")
        if not project_id:
            raise ValueError("CI_PROJECT_ID is not set in the environment")
        
        source_branch = os.getenv("CR_SOURCE_BRANCH")
        if not source_branch:
            raise ValueError("CR_SOURCE_BRANCH is not set in the environment")
        
        project = self.gl.projects.get(project_id)
        
        branch = project.branches.get(source_branch)
        
        latest_commit = branch.commit
        
        commit = project.commits.get(latest_commit['short_id'])
        
        for comment in comments:
            
            commit.comments.create({'note': comment.comment,
                'line': comment.start,
                'line_type': 'new',
                'path': comment.file_path})

    def commit_changes(self, source_branch, target_branch, commit_message, metadatas: List[dict]):
        project_id = os.getenv("CI_PROJECT_ID")
        if not project_id:
            raise ValueError("CI_PROJECT_ID is not set in the environment")
        
        project = self.gl.projects.get(project_id)
        
        for metadata in metadatas:
            path = metadata["file_path"]
            code = metadata["code"]
            
            if os.path.exists(path):
                action = "update"
            else:
                action = "create"
            
            # See https://docs.gitlab.com/ce/api/commits.html#create-a-commit-with-multiple-files-and-actions
            # for actions detail
            data = {
                'branch': target_branch,
                'start_branch': source_branch,
                'commit_message': commit_message,
                'actions': [
                    {
                        'action': action,                    
                        'file_path': path,
                        'content': code,
                    }
                ]
            }

            commit = project.commits.create(data)
            
            print(commit)
    
if __name__ == "__main__":
    
    gl = GitLabIntegration()
    
    os.environ.setdefault("CI_PROJECT_ID", "14106")
    os.environ.setdefault("CR_SOURCE_BRANCH", "gitlab-comments")
    os.environ.setdefault("CI_MERGE_REQUEST_ID", "gitlab-comments")
    
    #gl.commit_changes("gitlab-integration", "delete_me", "hey, it's a meeee... ", [{"file_path": "/test/blah.txt", "code": "Only a test"}])
    
    comments = []
    
    comments.append(CodeComment("Total garbage, as usual", 50, 53, "src/integrations/gitlab_integration.py"))
    
    gl.add_commit_comments(comments=comments)
    
    
    