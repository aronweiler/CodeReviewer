from typing import List
from abc import ABC, abstractmethod
from code_comment import CodeComment

class CommenterBase(ABC):
    @abstractmethod
    def add_comments(self, comments: List[CodeComment]):
        pass
