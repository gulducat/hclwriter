import logging
from copy import deepcopy
from typing import Iterable, Tuple

logger = logging.getLogger(__name__)


class Block:
    _total_count = 0  # TODO: remove?  or leave for "proviling" ??
    _instances = []

    def __init__(self, name: str):  # TODO: "name" -> "type" ?
        Block._total_count += 1
        self._name = name
        self._attrs = []  # TODO: "attrs" -> "names" ?
        self._args = ()
        self._kwargs = {}
        self._after_call_attrs = []
        self._called = False

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
        # TODO: is this ^ sifficient?
        # return all([
        #     getattr(self, attr) == getattr(other, attr, None)
        #     for attr in self.__dict__
        # ])

    def __copy__(self) -> 'Block':
        return deepcopy(self)  # TODO: cov missing

    def __deepcopy__(self, memo: dict) -> 'Block':
        cp = self.__class__(self._name)
        cp.__dict__ = deepcopy(self.__dict__, memo)
        return cp

    def __getattr__(self, attr: str) -> 'Block':
        # build the content of the hcl block
        if not self._called:
            self._attrs.append(attr)
            return self

        # for referencing blocks as values in other blocks
        # we make a copy so that _after_call_attrs is unique per reference
        cp = deepcopy(self)
        cp._after_call_attrs.append(attr)
        return cp

    __getitem__ = __getattr__

    def __call__(self, *args: Tuple['Block'], **kwargs) -> 'Block':
        for a in args:
            if not isinstance(a, Block):
                raise TypeError(
                    f'non-keyword arguments must be `Block`s, got {type(a)}: {a}'
                )
        if self._called:
            # make a copy, wipe its call args, call it and return it
            cp = deepcopy(self)
            cp._args = ()
            cp._kwargs = {}
            cp._called = False
            return cp(*args, **kwargs)
        else:
            self._args = args
            self._kwargs = kwargs
            self._called = True
            if self not in Block._instances:
                Block._instances.append(self)
        return self

    def __str__(self) -> str:
        w = HCLWriter(self._name, self._attrs, *self._args, **self._kwargs)
        return str(w)

    def __repr__(self) -> str:
        # TODO: is this a sensible non-terraform default?
        return '.'.join([self._name] + self._attrs + self._after_call_attrs)


class HCLWriter:  # TODO: how much of this is tf-specific?
    def __init__(self,
                 _block_type: str,
                 _block_names: Iterable[str],
                 *args, **kwargs):
        self.block_type = _block_type
        self.block_names = _block_names
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        # funny dance to remove extraneous newlines.
        # placed here instead of elsewhere, because it has full context
        # of the entire block string.
        # TODO: fix logic elsewhere instead?
        result = []
        lines = self.hcl.splitlines()
        for idx, line in enumerate(lines):
            if line == '' and lines[idx-1].endswith('}'):
                continue
            result.append(line)
        return '\n'.join(result) + '\n'

    # def write(self, *args, **kwargs):
    #     print(str(self))
    #     if args or kwargs:
    #         with open(*args, **kwargs) as f:
    #             f.write(str(self) + '\n')

    @property
    def hcl(self):
        block = self.block_type
        for n in self.block_names:
            block += ' "%s"' % n
        block += ' {'
        if not self.args and not self.kwargs:
            return block + '}'

        # named args first
        block += recurse(self.kwargs)

        # then nested blocks
        for a in self.args:
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
