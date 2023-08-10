from typing import List
from abc import ABC, abstractmethod
from code_review_tool import CodeComment

class CommenterBase(ABC):
    @abstractmethod
    def add_comments(self, comments: List[CodeComment]):
        pass
