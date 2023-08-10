import os
from llm_arguments import LLMArguments


class ReviewConfiguration:
    def __init__(self, provider, include_summary, llm_arguments) -> None:
        self.provider = provider
        self.include_summary = include_summary        
        self.llm_arguments = llm_arguments

    @staticmethod
    def from_json_file(file_path: str):
        import json

        with open(file_path, "r") as f:
            config = json.load(f)

        return ReviewConfiguration.from_dict(config)

    @staticmethod
    def from_environment():
        provider = os.environ.get("CR_PROVIDER", False)
        include_summary = os.environ.get("CR_INCLUDE_SUMMARY", "False").lower() == "true"

        llm_arguments = LLMArguments.from_environment()

        return ReviewConfiguration(provider, include_summary, llm_arguments)

    @staticmethod
    def from_dict(config: dict):
        provider = config.get("provider", None)        
        include_summary = config.get("include_summary", False)

        llm_arguments = LLMArguments.from_dict(config.get("llm", None))

        return ReviewConfiguration(provider, include_summary, llm_arguments)
