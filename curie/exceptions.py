# curie/exceptions.py


class CurieError(Exception):
    """Base exception for all Curie SDK errors."""
    pass


class AuthenticationError(CurieError):
    """Invalid or missing API key."""
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message)


class ModelNotFoundError(CurieError):
    """Requested model does not exist or is not available."""
    def __init__(self, model: str, available: list[str] | None = None):
        msg = f"Model '{model}' not found."
        if available:
            msg += f" Available models: {', '.join(available)}"
        super().__init__(msg)
        self.model = model
        self.available_models = available or []


class InferenceError(CurieError):
    """Inference failed on the server."""
    def __init__(self, message: str, job_id: str | None = None):
        super().__init__(message)
        self.job_id = job_id


class RateLimitError(CurieError):
    """Rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded. Please wait before retrying."):
        super().__init__(message)


class ValidationError(CurieError):
    """Input validation failed."""
    pass


class TimeoutError(CurieError):
    """Request timed out."""
    def __init__(self, model: str, timeout: int):
        super().__init__(f"Request to model '{model}' timed out after {timeout}s.")
        self.model = model
        self.timeout = timeout
