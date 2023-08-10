from typing import List
from langchain.tools import StructuredTool

class CodeComment:
    """A code comment."""
    
    def __init__(self, comment: str, start: int = None, end: int = None, file_path: str = None):
        self.start = start
        self.end = end
        self.comment = comment
        self.file_path = file_path

# class CodeReviewTool(StructuredTool):

#     def add_comment(starting_line_number: int, ending_line_number: int, comment_in_markdown):
#         """Add a comment to the code.
        
#         Args:
#             starting_line_number (int): The line number where the comment should start.
#             ending_line_number (int): The line number where the comment should end.
#             comment_in_markdown (str): The comment in Markdown."""
        
#         return [CodeComment(starting_line_number, ending_line_number, comment_in_markdown)]
    
#     def add_comment_list(comments:List[CodeComment]):
#         """Add a comment to the code.
        
#         Args:            
#             comments (List[CodeComment]): A list of comments to add to the code."""
        
#         return comments
    
