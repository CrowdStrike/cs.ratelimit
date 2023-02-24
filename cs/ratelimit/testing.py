"""Test helpers."""
from queue import LifoQueue
import logging

from zope.component.testlayer import ZCMLFileLayer

import cs.ratelimit


RATELIMIT_INTEGRATION_LAYER = ZCMLFileLayer(cs.ratelimit,
                                            zcml_file='ftesting.zcml',
                                            name='RatelimitComponents')


# Setup Queue (thread-safe memory) logging handler for test referencing (allows tests to review Queue)
# to check last entry:
# >>> 'My String' in logger_queue.get_nowait()
# True
logger_queue = LifoQueue()


class QueuingHandler(logging.Handler):
    """Provides LIFO access to handled log lines."""

    def __init__(self, *args, **kwargs):
        """Initialize by copying the queue and sending everything else to superclass."""
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        """Add the formatted log message (sans newlines) to the queue."""
        logger_queue.put(self.format(record).rstrip('\n'))


logging.getLogger().addHandler(QueuingHandler())
