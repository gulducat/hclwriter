from hclwriter import Block
from hclwriter import file

TerraformFile = file.HCLFile


class TerraformBlock(Block):
    def __str__(_self) -> str:
        if _self._name == 'comment':  # TODO: this is HACK
            return f'# {_self._kwargs["msg"]}'
        return super().__str__()

    def __repr__(_self) -> str:
        err = None  # TODO: stack trace from errors here are confusing...  just let tf handle it?

        if _self._name == 'variable':
            if len(_self._attrs) != 1:
                err = 'must have exactly 1 name'
            bits = ['var'] + _self._attrs

        elif _self._name == 'locals':
            bits = ['local'] + _self._attrs + _self._after_call_attrs

        elif _self._name == 'resource':
            bits = _self._attrs + _self._after_call_attrs

        elif _self._name == 'provider':
            bits = _self._attrs + [_self._kwargs['alias']]
            # bits = _self._attrs
            # if _self._kwargs.get('alias'):
            #     bits = bits + [_self._kwargs['alias']]

        else:
            return super(TerraformBlock, _self).__repr__()

        if err:
            raise NotImplementedError(
                f'{_self._name} {err}, got: {_self._attrs}'
            )

        return '.'.join(bits)
