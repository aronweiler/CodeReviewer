from typing import List
from abc import ABC, abstractmethod
from review.code_comment import CodeComment

class SourceControlBase(ABC):
    @abstractmethod
    def add_pr_comments(self, comments: List[CodeComment]):
        pass

    @abstractmethod
    def commit_changes(self, branch_name, commit_message, code_documents):
        pass

    @abstractmethod
    def create_branch(self, source_branch, target_branch):
        pass

    