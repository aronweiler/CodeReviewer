import os

class LLMArguments:
    def __init__(
        self,
        model,
        temperature,
        max_supported_tokens,
        max_completion_tokens
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
            config = {} # Use defaults

        model = config.get("model", "gpt-3.5-turbo-0613")
        temperature = config.get("temperature", "0")
        max_supported_tokens = config.get("max_supported_tokens", 4096)
        max_completion_tokens = config.get("max_completion_tokens", 2048)
        

        return LLMArguments(
            model, temperature, max_supported_tokens, max_completion_tokens
        )
