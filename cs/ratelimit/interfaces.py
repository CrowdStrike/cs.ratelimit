"""Interfaces used to connect the rate limiting components together."""
from datetime import datetime
import functools
import threading

from zope import interface
from zope import schema
from zope.interface.common.mapping import IReadMapping


def _is_rate_limiter_state_schema(rl_state):
    if 'updated' not in rl_state or 'counter' not in rl_state:
        raise schema.ValidationError("expected schema to contain 'updated' and 'counter' keys")
    if not isinstance(rl_state['updated'], datetime):
        raise schema.ValidationError(f"expected 'updated' value to be instance of {datetime}")
    if not isinstance(rl_state['counter'], int):
        raise schema.ValidationError(f"expected 'updated' value to be instance of {int}")
    return True


def _instanceis(classinfo, obj):
    return isinstance(obj, classinfo)


class IRateLimiterState(IReadMapping):  # pylint: disable=too-many-ancestors
    """A mapping containing keys for mutable internal rate limiter state.

    'updated': value is a datetime.datetime representing the last time the
               counter was updated
    'counter': An integer reflecting the number of calls made to the limiter
               after that last reset.
    """


class IRateLimitProperties(interface.Interface):  # pylint: disable=inherit-non-class
    """Call rate limit properties."""

    max_count = schema.Int(
            title="Max call count",
            description="Maximum amount of calls per interval, 0 indicates no limit",
            required=True,
            min=0
        )

    interval = schema.Timedelta(
            title="Time interval",
            description="minimum elapsed time span before internal rate counter is reset",
            required=True
        )

    block = schema.Bool(
            title="Call blocker",
            description="True indicates to block if max_count is reached before " +
                        "internalrate counter is reset.  If not set, a " +
                        "RateLimitExceeded is raised.",
            required=True
        )

    state = schema.Field(
            title="Rate limit state information",
            description="Contains mutable information tracking callable state",
            required=True,
            constraint=_is_rate_limiter_state_schema
        )

    rlock = schema.Field(
            title="Re-entrant threading lock",
            description="Lock to protect state access and mutation",
            required=True,
            constraint=functools.partial(_instanceis, type(threading.RLock()))
        )

    def mapping():  # pylint: disable=no-method-argument
        """Return schema attributes as key value pairs in a referenced dict instance."""
