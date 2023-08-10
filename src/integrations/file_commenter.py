import logging
import os
from typing import List
from github import Github
from github import Auth

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from integrations.commenter_base import CommenterBase, CodeComment


class FileCommenter(CommenterBase):
    def __init__(self):
        self.output = os.environ.get("FILE_OUTPUT", "output.md")

    def add_comments(self, comments: List[CodeComment]):

        last_file = ''
        output_string = ''
        for comment in comments:
            if comment.file_path != last_file:
                output_string += f"\n\n## {comment.file_path}\n"
                last_file = comment.file_path

            if comment.start != None:
                output_string +=  f"Lines: {comment.start}-{comment.end}: "
            
            output_string +=  comment.comment + "\n"

        with open(self.output, "w") as f:
            f.write(output_string)

