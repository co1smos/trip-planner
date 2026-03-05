class LLMError(Exception): 
    def __init__(self, message: str, type: str = "unknown", retryable: bool = False, details: dict | None = None):
        super().__init__(message)
        self.type = type
        self.retryable = retryable
        self.details = details


def is_retryable(e: Exception) -> bool: 
    if hasattr(e, "retryable"):
        return getattr(e, "retryable")
    return False