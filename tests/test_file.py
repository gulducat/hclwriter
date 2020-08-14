from textwrap import dedent
from unittest import TestCase
from unittest.mock import mock_open, patch

from hclwriter import Block
from hclwriter.file import HCLFile


class TestHCLFile(TestCase):
    b1 = Block('block1')()
    b2 = Block('block2')()
    expect = dedent('''\
    block1 {}

    block2 {}
    ''')

    def assert_calls(self, mo):
        mo.assert_called_with('test.hcl', 'w')
        mo().write.assert_called_with(self.expect)

    def test_additions(self):
        f = HCLFile(filename='forgetme.hcl')
        # will write() in order of addition
        f += self.b1
        f += self.b2

        with patch('builtins.open', mock_open()) as mo:
            f.write(filename='test.hcl')  # overrides __init__ filename
        self.assert_calls(mo)

    def test_subclass(self):
        class MyFile(HCLFile):
            _filename = 'test.hcl'
            # will write() in alphabetical order, not this order.
            b2 = self.b2
            b1 = self.b1

        f = MyFile()
        with patch('builtins.open', mock_open()) as mo:
            f.write()
        self.assert_calls(mo)

    def test_context_manager(self):
        with patch('builtins.open', mock_open()) as mo:
            with HCLFile(filename='test.hcl'):
                Block('block1')()
                Block('block2')()
        self.assert_calls(mo)

    def test_multiple_context_managers(self):
        # multiple should not step on each other,
        # and blocks outside the context manager should be ignored
        Block('ignore-me')()
        self.test_context_manager()
        self.test_context_manager()
