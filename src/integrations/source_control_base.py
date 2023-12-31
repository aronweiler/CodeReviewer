from typing import List
from abc import ABC, abstractmethod
from review.code_comment import CodeComment

class SourceControlBase(ABC):
    @abstractmethod
    def add_pr_comments(self, comments: List[CodeComment]):
        pass

    @abstractmethod
    def commit_changes(self, source_branch, target_branch, commit_message, metadatas: List[dict]):
        pass


    