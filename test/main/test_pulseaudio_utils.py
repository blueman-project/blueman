from unittest import TestCase

from blueman.main.PulseAudioUtils import PulseAudioUtils
from blueman.gobject import SingletonGObjectMeta


class TestPulseaudioUtils(TestCase):
    def test_metaclass(self):
        self.assertIsInstance(PulseAudioUtils, SingletonGObjectMeta)
