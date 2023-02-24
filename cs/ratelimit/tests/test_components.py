import unittest

from zope import component
from zope.interface.verify import verifyObject

from ..testing import RATELIMIT_INTEGRATION_LAYER
from ..components import RateLimitProperties
from ..interfaces import IRateLimitProperties


class UnitTestRatelimitProperties(unittest.TestCase):

    def test_init(self):
        rl_prop = RateLimitProperties()
        self.assertTrue(IRateLimitProperties.providedBy(rl_prop))
        rl_prop = RateLimitProperties(max_count=1)
        self.assertEqual(rl_prop.max_count, 1)

        verifyObject(IRateLimitProperties, rl_prop)


class IntegrationTestRatelimitProperties(unittest.TestCase):

    layer = RATELIMIT_INTEGRATION_LAYER

    def test_rl_properties_factory(self):
        rl_prop = component.createObject('cs.ratelimit.properties')
        self.assertTrue(IRateLimitProperties.providedBy(rl_prop))
