from anvil_test import TestAnvilLevel
from templevel import TempLevel

__author__ = 'Rio'

class TestMCR(TestAnvilLevel):
    def setUp(self):
        self.indevLevel = TempLevel("hell.mclevel")
        self.anvilLevel = TempLevel("PyTestWorld")

