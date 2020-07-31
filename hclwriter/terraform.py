from hclwriter import Block
from hclwriter.file import HCLFile

TerraformFile = HCLFile


class TerraformBlock(Block):
    def __repr__(self):
        if self._name == 'variable':
            bits = ['var'] + self._attrs
        elif self._name == 'locals':
            bits = ['local'] + self._attrs + self._after_call_attrs
        elif self._name == 'resource':
            bits = self._attrs + self._after_call_attrs
        elif self._name == 'provider':
            bits = self._attrs + [self._kwargs['alias']]
        else:
            return super(TerraformBlock, self).__repr__()
        return '.'.join(bits)
