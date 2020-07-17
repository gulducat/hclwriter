#!/usr/bin/env python

import json
import unittest

from hclwriter import HCLWriter


class TestHCLEr(unittest.TestCase):
    def setUp(self):
        with open("test.json") as f:
            self.data = json.load(f)
        with open("test.hcl") as f:
            self.expected = f.read()

    def test_str(self):
        h = HCLWriter(self.data)
        self.assertEqual(self.expected, str(h))
