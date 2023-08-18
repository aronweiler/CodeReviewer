from typing import List

from review.code_comment import CodeComment


class Diff:
    old_path: str
    new_path: str
    diff_content: str
    new_file: bool
    renamed_file: bool
    deleted_file: bool

    review_comments: List[CodeComment]
    
    def __init__(self, old_path, new_path, diff_content, new_file, renamed_file, deleted_file):
        self.old_path = old_path
        self.new_path = new_path
        self.diff_content = diff_content
        self.new_file = new_file
        self.renamed_file = renamed_file
        self.deleted_file = deleted_file
        
