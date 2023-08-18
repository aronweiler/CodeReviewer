from typing import List
from abc import ABC, abstractmethod
from review.code_comment import CodeComment
from integrations.diff import Diff

class SourceControlBase(ABC):
    @abstractmethod
    def get_pr_diffs(self) -> List[Diff]:
        pass
    
    @abstractmethod
    def add_pr_comments(self, comments: List[CodeComment]):
        pass
    
    @abstractmethod
    def add_commit_comments(self, comments: List[CodeComment]):
        pass

    @abstractmethod
    def commit_changes(self, source_branch, target_branch, commit_message, metadatas: List[dict]):
        pass