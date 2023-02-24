"""Custom exceptions for use with the rate limiting components and decorators."""


class RateLimitError(Exception):
    """A ratelimit error."""


class RateLimitExceeded(RateLimitError):
    """A rate limit has been exceeded."""
