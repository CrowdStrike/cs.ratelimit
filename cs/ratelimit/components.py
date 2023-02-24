"""Components that can be used to configure and construct rate limiting decorators."""
from datetime import datetime, timedelta
import threading

from zope import interface
from zope.component.factory import Factory
from zope.schema.fieldproperty import createFieldProperties

from .interfaces import IRateLimitProperties


@interface.implementer(IRateLimitProperties)
class RateLimitProperties:
    """Can be used to create per-instance vs per-class rate limiters.

    See usage examples in the README for more details.
    """

    # pylint: disable=too-many-arguments,too-few-public-methods
    createFieldProperties(IRateLimitProperties)

    def __init__(self, max_count=0, interval=timedelta(seconds=0),
                 block=False, state=None, rlock=None):
        """Set instance configuration and initialize mutable state.

        See `.interfaces.IRateLimitProperties` definition for detailed
        info about the accepted kwargs.
        """
        self.max_count = max_count if max_count else 0
        self.interval = interval if interval else timedelta(seconds=0)
        self.block = block if block else False
        self.state = state if state is not None else {
          'updated': datetime.min,
          'counter': 0
        }
        self.rlock = rlock if rlock else threading.RLock()

    def mapping(self):
        """Satisfies `IRateLimitProperties` by providing internal state in a `mapping` attr."""
        return self.__dict__


RateLimitPropertiesFactory = Factory(RateLimitProperties)


@interface.implementer(IRateLimitProperties)
def ratelimitproperties_factory(**kwargs):
    """Create per-instance rate limiters from text-based config.

    Essentially same as RateLimitProperties, except interval can be
    an integer or float that will be converted into a timedelta based on
    seconds.
    """
    if 'interval' in kwargs and not isinstance(kwargs['interval'], timedelta):
        kwargs['interval'] = timedelta(seconds=kwargs['interval'])
    return RateLimitProperties(**kwargs)


ConfigRateLimitPropertiesFactory = Factory(ratelimitproperties_factory)
