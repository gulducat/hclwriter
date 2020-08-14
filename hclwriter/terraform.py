from hclwriter import Block
from hclwriter import file

TerraformFile = file.HCLFile


class TerraformBlock(Block):
    def __str__(self) -> str:
        if self._name == 'comment':  # TODO: this is HACK
            return f'# {self._kwargs["msg"]}'
        return super().__str__()

    def __repr__(self) -> str:
        err = None  # TODO: stack trace from errors here are confusing...  just let tf handle it?

        if self._name == 'variable':
            if len(self._attrs) != 1:
                err = 'must have exactly 1 name'
            bits = ['var'] + self._attrs

        elif self._name == 'locals':
            bits = ['local'] + self._attrs + self._after_call_attrs

        elif self._name == 'resource':
            bits = self._attrs + self._after_call_attrs

        elif self._name == 'provider':
            bits = self._attrs + [self._kwargs['alias']]
            # bits = self._attrs
            # if self._kwargs.get('alias'):
            #     bits = bits + [self._kwargs['alias']]

        else:
            return super(TerraformBlock, self).__repr__()

        if err:
            raise NotImplementedError(
                f'{self._name} {err}, got: {self._attrs}'
            )

        return '.'.join(bits)
