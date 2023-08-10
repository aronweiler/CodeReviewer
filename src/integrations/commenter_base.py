from abc import ABC, abstractmethod
from code_review_tool import CodeComment

class CommenterBase(ABC):
    @abstractmethod
    def add_comments(self, comment:CodeComment):
        pass
