"""This module provides most of the public API for cs.ratelimit.

See the README for more info and usage examples.
"""
from datetime import datetime, timedelta
import functools
import logging
import threading
import time

from .exceptions import RateLimitExceeded


logger = logging.getLogger(__name__)


def ratelimited(**kwargs):
    """Threadsafe decorator to limit rate of Python callables for unbound functions.

    max_count, interval, and block may be adjusted at runtime safely.  Default
    initialization values do not limit call rate.  If either max_count
    or interval evaluate to False, call rate is not limited.

    Kwargs:
        max_count: maximum integer number of calls per interval
        interval: either int/long/float (seconds) or datetime.timedelta
                  representing minimum elapsed time span before internal
                  rate counter is reset.  Minimum non-zero interval
                  evaluation is determined by Python datetime.timedelta.
        block: True indicates to block if max_count is reached before internal
               rate counter is reset.  If not set, a
               RateLimitExceeded is raised.

    Use-cases
     * dev decorates class method with/without code-time limits
     * dev decorates c/python function with/without code-time limits
     * runtime assignment of decorated limit specs
     * runtime 'over-ride' of instance-specific limit specs

    Implementation:
     Decorator descriptor class 'RateLimit' (non-data descriptors __dict__ lookups
     have precedence over __get__() )
      * If we want to prevent the descriptor for getting called, we can over-ride
        __getattribute__()
      * class-call to __get__()
      * instance-call to __get__()
      * manages decorator-instance default limits in function-variables
      * assigns default values (non-limiting) to these ^^
      * runtime can re-assign via <ratelimit-instance>.block = True, etc
      * doesn't assign specs (e.g. uses defaults which don't limit)
    """
    return functools.partial(_rate_limited, **kwargs)


def ratelimitedmethod(*args, **kwargs):
    """Threadsafe decorator like `ratelimited` but for instance methods."""
    if args:  # assumes callable producing IRateLimitProperties provider
        kwargs = {
            'max_count': lambda self: args[0](self).mapping()['max_count'],
            'interval': lambda self: args[0](self).mapping()['interval'],
            'block': lambda self: args[0](self).mapping()['block'],
            'state': lambda self: args[0](self).mapping()['state'],
            'rlock': lambda self: args[0](self).mapping()['rlock'],
        }
    return functools.partial(_rate_limited_method, **kwargs)


def _rate_limited(func, **kwargs):
    # setup closure params
    max_count = kwargs['max_count'] if 'max_count' in kwargs else 0
    interval = kwargs['interval'] if 'interval' in kwargs else timedelta(seconds=0)
    block = kwargs['block'] if 'block' in kwargs else False
    state = kwargs['state'] if 'state' in kwargs else None
    rlock = kwargs['rlock'] if 'rlock' in kwargs else None

    # set appropriate default mutable types for state and lock.
    if state is None:
        state = {'updated': datetime.min,
                 'counter': 0}
    if rlock is None:
        rlock = threading.RLock()

    # turn all param access into callables
    def call(value):
        return value
    if not callable(max_count):
        max_count = functools.partial(call, max_count)
    if not callable(interval):
        interval = functools.partial(call, interval)
    if not callable(block):
        block = functools.partial(call, block)
    if not callable(state):
        state = functools.partial(call, state)
    if not callable(rlock):
        rlock = functools.partial(call, rlock)

    @functools.wraps(func)
    def rate_limited(*args, **kwargs):
        with rlock():
            _max_count, _interval, _block, _state = \
                                    max_count(), interval(), block(), state()

            if not _state['updated']:
                _state['updated'] = datetime.min
            if not _state['counter']:
                _state['counter'] = 0

            if _max_count and _state['counter'] >= _max_count:
                gap = (_state['updated'] + _interval) - datetime.now()
                if _interval and gap.total_seconds() > 0:
                    if not _block:
                        raise RateLimitExceeded(
                            f"attempt to exceed rate limit of {func} with {_max_count} calls per "
                            f"{_interval} timedelta was made.")
                    logger.debug("Call limit exceeded, sleeping %s seconds", gap.total_seconds())
                    time.sleep(gap.total_seconds())
                logger.debug("ratelimit counter reset due to exceeded time interval of %s", _interval)
                _state['counter'] = 0  # reset

            _state['counter'] += 1
            _state['updated'] = datetime.now()
            logger.debug("counter for %s is now %s of %s", rate_limited, _state['counter'], _max_count)

        logger.debug("calling %s with args <%s> and kwargs <%s>", func, args, kwargs)
        return func(*args, **kwargs)

    rate_limited.__wrapped__ = func  # setup external bypass

    return rate_limited


def _rate_limited_method(func, **kwargs):
    # setup closure params
    max_count = kwargs['max_count'] if 'max_count' in kwargs else 0
    interval = kwargs['interval'] if 'interval' in kwargs else timedelta(seconds=0)
    block = kwargs['block'] if 'block' in kwargs else False
    state = kwargs['state'] if 'state' in kwargs else None
    rlock = kwargs['rlock'] if 'rlock' in kwargs else None

    # set appropriate default mutable types for state and lock.
    if state is None:
        state = {'updated': datetime.min,
                 'counter': 0}
    if rlock is None:
        rlock = threading.RLock()

    # turn all param access into callables
    def call(value, _):
        return value
    if not callable(max_count):
        max_count = functools.partial(call, max_count)
    if not callable(interval):
        interval = functools.partial(call, interval)
    if not callable(block):
        block = functools.partial(call, block)
    if not callable(state):
        state = functools.partial(call, state)
    if not callable(rlock):
        rlock = functools.partial(call, rlock)

    @functools.wraps(func)
    def rate_limited(*args, **kwargs):
        self = args[0]
        with rlock(self):
            _max_count, _interval, _block, _state = \
                                max_count(self), interval(self), block(self), state(self)

            if not _state['updated']:
                _state['updated'] = datetime.min
            if not _state['counter']:
                _state['counter'] = 0

            if _max_count and _state['counter'] >= _max_count:
                gap = (_state['updated'] + _interval) - datetime.now()
                if _interval and gap.total_seconds() > 0:
                    if not _block:
                        raise RateLimitExceeded(
                            f"attempt to exceed rate limit of {func} with {_max_count} calls per "
                            f"{_interval} timedelta was made.")
                    logger.debug("Call limit exceeded, sleeping %s seconds", gap.total_seconds())
                    time.sleep(gap.total_seconds())
                logger.debug("ratelimit counter reset due to exceeded time interval of %s", _interval)
                _state['counter'] = 0  # reset

            _state['counter'] += 1
            _state['updated'] = datetime.now()
            logger.debug("state for ratelimit %s is now %s with max count of %s", rate_limited, _state, _max_count)

        logger.debug("calling %s with args <%s> and kwargs <%s>", func, args, kwargs)
        return func(*args, **kwargs)

    rate_limited.__wrapped__ = func  # setup external bypass
    return rate_limited
