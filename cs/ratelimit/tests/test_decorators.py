from datetime import timedelta, datetime
import logging
import threading
import unittest

from ..components import RateLimitProperties
from ..decorators import _rate_limited, ratelimited, _rate_limited_method, ratelimitedmethod
from ..exceptions import RateLimitExceeded
from ..testing import logger_queue


class UnitTestRatelimited(unittest.TestCase):
    logger = logging.getLogger('cs.ratelimit.decorators')

    def setUp(self):
        self.logger_level_orig = self.logger.getEffectiveLevel()

    def tearDown(self):
        self.logger.setLevel(self.logger_level_orig)
        while not logger_queue.empty():
            logger_queue.get_nowait()

    def test_wrapper(self):
        def my_callable():
            """My callable docstring"""
        rl = _rate_limited(my_callable)
        self.assertEqual('My callable docstring', rl.__doc__)
        self.assertIs(rl.__wrapped__, my_callable)

    def test_unlimited(self):
        def my_callable():
            pass
        rl = _rate_limited(my_callable)  # default is unlimited
        self.logger.setLevel(logging.DEBUG)
        rl()
        rl()
        self.assertNotIn('Call limit exceeded, sleeping', logger_queue.get_nowait())

    def test_limited(self):
        def my_callable():
            pass
        # blocking
        rl = _rate_limited(
                my_callable, max_count=1,
                interval=timedelta(seconds=.1), block=True)
        self.logger.setLevel(logging.DEBUG)
        rl()
        rl()
        # pop 3 messages (args/kwargs list, counter state, and reset after sleep)
        logger_queue.get_nowait()
        logger_queue.get_nowait()
        logger_queue.get_nowait()
        self.assertIn('Call limit exceeded, sleeping', logger_queue.get_nowait())
        # exception
        rl = _rate_limited(
                my_callable, max_count=1,
                interval=timedelta(seconds=.1), block=False)
        rl()
        with self.assertRaises(RateLimitExceeded):
            rl()

    def test_external_state(self):
        n = datetime.now()
        state = {'counter': 1, 'updated': n}

        def my_callable():
            pass
        rl = _rate_limited(
                my_callable, max_count=1,
                interval=timedelta(seconds=.1), block=True, state=state)
        rl()
        self.assertNotEqual(n, state['updated'])

    def test_callable_input(self):
        def my_callable():
            pass
        rl = _rate_limited(
                my_callable, max_count=lambda: 1,
                interval=timedelta(seconds=.1), block=True)
        self.logger.setLevel(logging.DEBUG)
        rl()
        rl()
        # pop 3 messages (args/kwargs list, counter state, and reset after sleep)
        logger_queue.get_nowait()
        logger_queue.get_nowait()
        logger_queue.get_nowait()
        self.assertIn('Call limit exceeded, sleeping', logger_queue.get_nowait())

    def test_decoration(self):
        @_rate_limited
        def my_callable():
            pass
        self.logger.setLevel(logging.DEBUG)
        my_callable()
        self.assertIn('calling ', logger_queue.get_nowait())

    def test_decorator_factory(self):
        @ratelimited(max_count=1, interval=timedelta(seconds=.1), block=False)
        def my_callable():
            pass
        my_callable()
        with self.assertRaises(RateLimitExceeded):
            my_callable()

    def test_syncronization(self):
        @ratelimited(max_count=1, interval=timedelta(seconds=.1), block=True)
        def my_callable():
            pass
        t = datetime.now()
        t1 = threading.Thread(target=my_callable)
        t2 = threading.Thread(target=my_callable)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertGreaterEqual(datetime.now() - t, timedelta(seconds=.1))


class UnitTestRatelimitedMethod(unittest.TestCase):
    logger = logging.getLogger('cs.ratelimit.decorators')

    def setUp(self):
        self.logger_level_orig = self.logger.getEffectiveLevel()

    def tearDown(self):
        self.logger.setLevel(self.logger_level_orig)
        while not logger_queue.empty():
            logger_queue.get_nowait()

    def test_wrapper(self):
        class MyClass:
            def my_callable(self):
                """My callable docstring"""

        rl = _rate_limited_method(MyClass.my_callable)
        self.assertEqual("My callable docstring", rl.__doc__)

    def test_instance(self):
        class MyClass:
            def my_callable(self):
                pass

        # unlimited
        rl = _rate_limited_method(MyClass.my_callable)
        instance1 = MyClass()
        self.logger.setLevel(logging.DEBUG)
        rl(instance1)
        rl(instance1)
        self.assertNotIn("Call limit exceeded, sleeping", logger_queue.get_nowait())

        # exception
        rl = _rate_limited_method(MyClass.my_callable, max_count=1, interval=timedelta(seconds=1))
        rl(instance1)
        with self.assertRaises(RateLimitExceeded):
            rl(instance1)

    def test_non_callable_decorator_params(self):
        class MyClass:
            @ratelimitedmethod(max_count=1, interval=timedelta(seconds=1), block=False)
            def my_callable(self):
                pass

        instance1 = MyClass()
        instance1.my_callable()
        with self.assertRaises(RateLimitExceeded):
            instance1.my_callable()

    def test_callable_decorator_params(self):
        from operator import attrgetter as a

        class MyClass:
            def __init__(self):
                self.max_count = 1
                self.interval = timedelta(seconds=1)
                self.block = False

            @ratelimitedmethod(max_count=a('max_count'),
                               interval=a('interval'),
                               block=a('block'))
            def my_callable(self):
                pass

        instance1 = MyClass()
        instance1.my_callable()
        with self.assertRaises(RateLimitExceeded):
            instance1.my_callable()

    def test_syncronization(self):
        class MyClass:
            @ratelimitedmethod(max_count=1, interval=timedelta(seconds=.1), block=True)
            def my_callable(self):
                pass

        instance1 = MyClass()
        t = datetime.now()
        t1 = threading.Thread(target=instance1.my_callable)
        t2 = threading.Thread(target=instance1.my_callable)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertGreaterEqual(datetime.now() - t, timedelta(seconds=.1))

    def test_rate_limit_property_member(self):
        from operator import attrgetter as a

        class MyClass:
            def __init__(self):
                self.rl = RateLimitProperties(max_count=1,
                                              interval=timedelta(seconds=1),
                                              block=False)

            @ratelimitedmethod(a('rl'))
            def my_callable(self):
                pass

        instance1 = MyClass()
        instance1.my_callable()
        with self.assertRaises(RateLimitExceeded):
            instance1.my_callable()
