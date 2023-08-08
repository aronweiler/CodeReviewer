class LLMArguments:
    def __init__(
        self,
        model,
        temperature,
        max_supported_tokens,
        max_completion_tokens,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_supported_tokens = max_supported_tokens
        self.max_completion_tokens = max_completion_tokens

    @staticmethod
    def from_dict(config: dict, tools):
        model = config["model"]
        temperature = config["temperature"]
        max_supported_tokens = config["max_supported_tokens"]
        max_completion_tokens = config["max_completion_tokens"]

        return LLMArguments(
            model, temperature, max_supported_tokens, max_completion_tokens, tools
        )
