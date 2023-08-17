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
        raise NotImplementedError("GitLabIntegration.add_pr_comments is not implemented")

    def commit_changes(self, source_branch, target_branch, commit_message, metadatas: List[dict]):
        project_id = os.getenv("GITLAB_PROJECT_ID")
        if not project_id:
            raise ValueError("GITLAB_PROJECT_ID is not set in the environment")
        
        for metadata in metadatas:
            path = metadata["file_path"]
            code = metadata["code"]

            project = self.gl.projects.get(project_id)
            # See https://docs.gitlab.com/ce/api/commits.html#create-a-commit-with-multiple-files-and-actions
            # for actions detail
            data = {
                'branch': target_branch,
                'start_branch': source_branch,
                'commit_message': commit_message,
                'actions': [
                    {
                        'action': 'create',                    
                        'file_path': path,
                        'content': code,
                    }
                ]
            }

            commit = project.commits.create(data)
    
        