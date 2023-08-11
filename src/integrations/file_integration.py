import logging
import os

from typing import List
from github import Github
from github import Auth

from langchain.schema import Document

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from integrations.source_control_base import SourceControlBase, CodeComment


class FileIntegration(SourceControlBase):
    def __init__(self):
        self.output = os.environ.get("FILE_OUTPUT", "output.md")

    def create_refactor_branch(self, source_branch: str, target_branch: str, files):       
        pass

    def commit_changes(self, branch_name:str, commit_message:str, code_documents:List[Document]):
        # Write the modified code out to the file system
        for i in range(0, len(code_documents['metadatas'])):
            path = code_documents['metadatas'][i]['file_name'] + ".refactored"
            
            # If the path exists, just append the new code to the end of the file
            if os.path.exists(path):
                with open(path, 'a') as file:
                    file.write(code_documents['metadatas'][i]['refactored_code'])
            # Otherwise, create a new file
            else:
                with open(path, 'w') as file:
                    file.write(code_documents['metadatas'][i]['refactored_code'])

    def create_branch(self, source_branch: str, target_branch: str):
        pass    

    def add_pr_comments(self, comments: List[CodeComment]):

        last_file = ''
        output_string = ''
        for comment in comments:
            if comment.file_path != last_file:
                output_string += f"\n\n## {comment.file_path}\n"
                last_file = comment.file_path

            if comment.start != None:
                output_string +=  f"- **Lines: {comment.start}-{comment.end}**: "
            
            output_string +=  comment.comment + "\n"

        with open(self.output, "w") as f:
            f.write(output_string)

