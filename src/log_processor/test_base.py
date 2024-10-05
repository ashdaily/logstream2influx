import unittest
import logging


class TestBase(unittest.TestCase):
    def setUp(self) -> None:
        logging.disable(logging.DEBUG)
