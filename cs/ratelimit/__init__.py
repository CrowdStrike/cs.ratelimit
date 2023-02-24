"""Ratelimit provides threadsafe APIs for limiting the frequency of Python callables.

This can be particular useful for taking advantage of the
[Decorator](https://refactoring.guru/design-patterns/decorator) software architecture
pattern to manage client-side rate limiting for 3rd party APIs and services independently
from your application logic.
"""
from .interfaces import IRateLimitProperties

from .components import RateLimitProperties
from .components import ratelimitproperties_factory

from .decorators import ratelimited
from .decorators import ratelimitedmethod

from .exceptions import RateLimitError
from .exceptions import RateLimitExceeded


__all__ = [
    'IRateLimitProperties', 'RateLimitProperties', 'ratelimitproperties_factory', 'ratelimited',
    'ratelimitedmethod', 'RateLimitError', 'RateLimitExceeded',
]
