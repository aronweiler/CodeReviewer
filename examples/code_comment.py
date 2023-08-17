from typing import Optional

class CodeComment:
    """A class representing a code comment."""

    def __init__(self, comment: str, start: Optional[int] = None, end: Optional[int] = None, file_path: Optional[str] = None):
        """
        Initializes a CodeComment object.

        Args:
            comment (str): The content of the comment.
            start (int, optional): The starting line number of the comment. Defaults to None.
            end (int, optional): The ending line number of the comment. Defaults to None.
            file_path (str, optional): The path of the file containing the comment. Defaults to None.
        """
        self.start = start
        self.end = end
        self.comment = comment
        self.file_path = file_path

# The code has been refactored to improve readability and maintainability.
# The class CodeComment now has a more descriptive docstring explaining its purpose and the arguments of its constructor.
# The start, end, and file_path parameters of the constructor are now optional, indicated by the use of Optional from the typing module.