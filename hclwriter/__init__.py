import logging
from copy import deepcopy
from typing import Iterable, Tuple

logger = logging.getLogger(__name__)


class Block:
    _total_count = 0  # TODO: remove?  or leave for "proviling" ??
    _instances = []

    def __init__(_self, name: str):  # TODO: "name" -> "type" ?
        Block._total_count += 1
        _self._name = name
        _self._attrs = []  # TODO: "attrs" -> "names" ?
        _self._args = ()
        _self._kwargs = {}
        _self._after_call_attrs = []
        _self._called = False

    def __eq__(_self, other):
        return _self.__dict__ == other.__dict__
        # TODO: is this ^ sifficient?
        # return all([
        #     getattr(_self, attr) == getattr(other, attr, None)
        #     for attr in _self.__dict__
        # ])

    def __copy__(_self) -> 'Block':
        return deepcopy(_self)  # TODO: cov missing

    def __deepcopy__(_self, memo: dict) -> 'Block':
        cp = _self.__class__(_self._name)
        cp.__dict__ = deepcopy(_self.__dict__, memo)
        return cp

    def __getattr__(_self, attr: str) -> 'Block':
        # build the content of the hcl block
        if not _self._called:
            _self._attrs.append(attr)
            return _self

        # for referencing blocks as values in other blocks
        # we make a copy so that _after_call_attrs is unique per reference
        cp = deepcopy(_self)
        cp._after_call_attrs.append(attr)
        return cp

    __getitem__ = __getattr__

    def __call__(_self, *args: Tuple['Block'], **kwargs) -> 'Block':
        for a in args:
            if not isinstance(a, Block):
                raise TypeError(
                    f'non-keyword arguments must be `Block`s, got {type(a)}: {a}'
                )
        if _self._called:
            # make a copy, wipe its call args, call it and return it
            cp = deepcopy(_self)
            cp._args = ()
            cp._kwargs = {}
            cp._called = False
            return cp(*args, **kwargs)
        else:
            _self._args = args
            _self._kwargs = kwargs
            _self._called = True
            if _self not in Block._instances:
                Block._instances.append(_self)
        return _self

    def __str__(_self) -> str:
        w = HCLWriter(_self._name, _self._attrs, *_self._args, **_self._kwargs)
        return str(w)

    def __repr__(_self) -> str:
        # TODO: is this a sensible non-terraform default?
        return '.'.join([_self._name] + _self._attrs + _self._after_call_attrs)


class HCLWriter:  # TODO: how much of this is tf-specific?
    def __init__(_self,
                 _block_type: str,
                 _block_names: Iterable[str],
                 *args, **kwargs):
        _self.block_type = _block_type
        _self.block_names = _block_names
        _self.args = args
        _self.kwargs = kwargs

    def __str__(_self) -> str:
        # funny dance to remove extraneous newlines.
        # placed here instead of elsewhere, because it has full context
        # of the entire block string.
        # TODO: fix logic elsewhere instead?
        result = []
        lines = _self.hcl.splitlines()
        for idx, line in enumerate(lines):
            if line == '' and lines[idx-1].endswith('}'):
                continue
            result.append(line)
        return '\n'.join(result) + '\n'

    # def write(_self, *args, **kwargs):
    #     print(str(_self))
    #     if args or kwargs:
    #         with open(*args, **kwargs) as f:
    #             f.write(str(_self) + '\n')

    @property
    def hcl(_self):
        block = _self.block_type
        for n in _self.block_names:
            block += ' "%s"' % n
        block += ' {'
        if not _self.args and not _self.kwargs:
            return block + '}'

        # named args first
        block += recurse(_self.kwargs)

        # then nested blocks
        for a in _self.args:
            if not block.endswith('{'):
                block += '\n'
            block += '\n'
            for line in str(a).splitlines():
                if line == '':
                    block += '\n'  # TODO: cov missing
                else:
                    block += '  %s\n' % line

        block += '\n}\n'
        return block


def recurse(val: dict, level: int = 1):
    content = ''
    indent = '  ' * level
    for k, v in val.items():
        if isinstance(v, list):
            content += '\n%s%s = [' % (indent, k)
            if len(v) == 0:
                content += ']'
                continue
            for x in v:
                content += '\n%s%s,' % (indent + '  ', format(x))
            content += '\n%s]' % indent
        elif isinstance(v, dict):
            content += '\n%s%s = {' % (indent, k)
            if len(v) == 0:
                content += '}'
                continue
            content += recurse(v, level=level + 1)
            content += '\n%s}' % indent
        else:
            content += '\n%s%s = %s' % (indent, k, format(v))
    return content


def format(val):
    # https://www.terraform.io/docs/configuration/types.html

    # TODO: Warning: Quoted type constraints are deprecated.
    #       for variables, ex: "string" -- TF("string") works though,
    #       and TF("map(string)"), and TF("concat()") and such.
    if isinstance(val, Block):
        return repr(val)
    elif isinstance(val, str):
        return '"%s"' % val
    elif isinstance(val, bool):
        return 'true' if val else 'false'
    return val
