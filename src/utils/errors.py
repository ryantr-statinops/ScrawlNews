class ScrawlError(Exception):
    """Domain failure with a fixed public message and explicit retry policy.

    Exception details and chained provider errors are for internal diagnostics only.
    """

    public_message = "Operation failed"

    def __init__(self, message: str = "", *, retryable: bool = False):
        super().__init__(message or self.public_message)
        self.retryable = retryable


class ScrawlerError(ScrawlError):
    public_message = "News source unavailable"


class SynthesizerError(ScrawlError):
    public_message = "Summarization unavailable"


class MessengerError(ScrawlError):
    public_message = "Message delivery failed"


class NotFoundError(ScrawlError):
    public_message = "Resource not found"


class ConfigError(ScrawlError):
    public_message = "Invalid configuration"
