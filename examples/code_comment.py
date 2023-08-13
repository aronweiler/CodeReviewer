from typing import Optional
from langchain.tools import StructuredTool

class CodeComment:
    """
    A class to represent a code comment.
    
    Attributes
    ----------
    start : int
        the starting line number of the comment in the code file
    end : int
        the ending line number of the comment in the code file
    comment : str
        the text of the comment
    file_path : str
        the path of the code file where the comment is located

    Methods
    -------
    __init__(self, comment: str, start: Optional[int] = None, end: Optional[int] = None, file_path: Optional[str] = None)
        Constructs all the necessary attributes for the code comment object.
    """

    def __init__(self, comment: str, start: Optional[int] = None, end: Optional[int] = None, file_path: Optional[str] = None):
        """
        Constructs all the necessary attributes for the code comment object.

        Parameters
        ----------
            comment : str
                the text of the comment
            start : int, optional
                the starting line number of the comment in the code file (default is None)
            end : int, optional
                the ending line number of the comment in the code file (default is None)
            file_path : str, optional
                the path of the code file where the comment is located (default is None)
        """

        self.start = start
        self.end = end
        self.comment = comment
        self.file_path = file_path