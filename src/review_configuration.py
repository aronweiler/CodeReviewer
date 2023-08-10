import os
import logging
import json
from llm_arguments import LLMArguments
from integrations.github_commenter import GitHubCommenter
from integrations.file_commenter import FileCommenter

PROVIDERS = {"github": GitHubCommenter(), "gitlab": None, "bitbucket": None, "file": FileCommenter()}

class ReviewConfiguration:
    def __init__(self, provider, include_summary, llm_arguments) -> None:
        self.provider = provider
        self.include_summary = include_summary        
        self.llm_arguments = llm_arguments

    @staticmethod
    def from_json_file(file_path: str):
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            logging.warn(f"Could not find configuration file at {file_path}, defaults will be used.")        
            return ReviewConfiguration.from_dict({})

        return ReviewConfiguration.from_dict(config)

    @staticmethod
    def from_environment():
        
        provider = os.environ.get("CR_PROVIDER", "file")
        if provider.lower() not in PROVIDERS:
            logging.error(f"Provider {provider} is not supported.")
            raise ValueError(f"Provider {provider} is not supported.")

        include_summary = os.environ.get("CR_INCLUDE_SUMMARY", "false").lower() == "true"

        llm_arguments = LLMArguments.from_environment()

        return ReviewConfiguration(provider, include_summary, llm_arguments)

    @staticmethod
    def from_dict(config: dict):
        provider = config.get("provider", None)        
        if provider.lower() not in PROVIDERS:
            logging.error(f"Provider {provider} is not supported.")
            raise ValueError(f"Provider {provider} is not supported.")
        
        include_summary = config.get("include_summary", False)

        llm_node = config.get("llm", None)
        if llm_node is None:
            logging.warn("No LLM configuration found, using defaults.")
            llm_node = {}

        llm_arguments = LLMArguments.from_dict(llm_node)

        return ReviewConfiguration(provider, include_summary, llm_arguments)
