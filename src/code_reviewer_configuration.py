import os
import logging
import json
from typing import Union, Dict
from integrations.github_integration import GitHubIntegration
from integrations.file_integration import FileIntegration
from integrations.source_control_base import SourceControlBase

PROVIDERS:Union[Dict[str,SourceControlBase], None] = {
    "github": GitHubIntegration(),
    "gitlab": None,
    "bitbucket": None,
    "file": FileIntegration(),
}

class CodeReviewerConfiguration:
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
            logging.warn(
                f"Could not find configuration file at {file_path}, defaults will be used."
            )
            return CodeReviewerConfiguration.from_dict({})

        return CodeReviewerConfiguration.from_dict(config)

    @staticmethod
    def from_environment():
        provider = os.environ.get("CR_PROVIDER", "file")
        if provider.lower() not in PROVIDERS:
            logging.error(f"Provider {provider} is not supported.")
            raise ValueError(f"Provider {provider} is not supported.")

        include_summary = (
            os.environ.get("CR_INCLUDE_SUMMARY", "false").lower() == "true"
        )

        llm_arguments = LLMArguments.from_environment()

        return CodeReviewerConfiguration(provider, include_summary, llm_arguments)

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

        return CodeReviewerConfiguration(provider, include_summary, llm_arguments)


class LLMArguments:
    def __init__(
        self, model, temperature, max_supported_tokens, max_completion_tokens
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_supported_tokens = max_supported_tokens
        self.max_completion_tokens = max_completion_tokens

    @staticmethod
    def from_json_file(file_path: str):
        import json

        with open(file_path, "r") as f:
            config = json.load(f)

        return LLMArguments.from_dict(config["llm"])

    @staticmethod
    def from_environment():
        model = os.environ.get("CR_MODEL", "gpt-3.5-turbo-0613")
        temperature = float(os.environ.get("CR_TEMPERATURE", "0"))
        max_supported_tokens = int(os.environ.get("CR_MAX_SUPPORTED_TOKENS", 4096))
        max_completion_tokens = int(os.environ.get("CR_MAX_COMPLETION_TOKENS", 2048))

        return LLMArguments(
            model, temperature, max_supported_tokens, max_completion_tokens
        )

    @staticmethod
    def from_dict(config: dict):
        if config is None:
            config = {}  # Use defaults

        model = config.get("model", "gpt-3.5-turbo-0613")
        temperature = config.get("temperature", "0")
        max_supported_tokens = config.get("max_supported_tokens", 4096)
        max_completion_tokens = config.get("max_completion_tokens", 2048)

        return LLMArguments(
            model, temperature, max_supported_tokens, max_completion_tokens
        )
