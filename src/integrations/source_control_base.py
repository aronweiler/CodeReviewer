from typing import List
from abc import ABC, abstractmethod
from review.code_comment import CodeComment

class SourceControlBase(ABC):
    @abstractmethod
    def add_pr_comments(self, comments: List[CodeComment]):
        pass

    @abstractmethod
    def create_refactor_branch(self, source_branch: str, target_branch: str, files):
        pass