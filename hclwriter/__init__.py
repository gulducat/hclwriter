import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

# TODO: type hinting (ignore python2)
# TODO: json? https://www.terraform.io/docs/configuration/syntax-json.html


class Block:
    _count = 0  # TODO: remove?  or leave for "proviling" ??

    def __init__(self, name: str):
        Block._count += 1
        self._name = name
        self._attrs = []
        self._args = ()
        self._kwargs = {}
        self._after_call_attrs = []
        self._called = False

    def __copy__(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        cp = self.__class__(self._name)
        cp.__dict__ = deepcopy(self.__dict__)
        return cp

    def __getattr__(self, attr):
        # build the content of the hcl block
        if not self._called:
            self._attrs.append(attr)
            return self

        # for referencing blocks as values in other blocks
        # we make a copy so that _after_call_attrs is unique per reference
        # TODO: return a BlockReference instead?  premature optimization
        cp = deepcopy(self)
        cp._after_call_attrs.append(attr)
        return cp

    __getitem__ = __getattr__

    def __call__(self, *a, **kw):
        if self._called:
            raise NotImplementedError('Block parameters already locked in.')
        else:
            self._args = a
            self._kwargs = kw
            self._called = True
        # TODO: return a FinalizedBlock?
        return self

    @property
    def _writer(self):
        return HCLWriter(self._name, self._attrs, *self._args, **self._kwargs)

    def __str__(self):
        return str(self._writer)

    def __repr__(self):
        # TODO: is this a sensible non-terraform default?
        return '.'.join([self._name] + self._attrs + self._after_call_attrs)

    def _write(self, *a, **kw):
        self._writer.write(*a, **kw)


class HCLWriter:
    def __init__(self, _block_type, _block_names, *a, **kw):
        self.converted = convert(_block_type, _block_names, *a, **kw)

    def __str__(self):
        # funny dance to remove extraneous newlines.
        # placed here instead of elsewhere, because it has full context
        # of the entire block string.
        # TODO: fix logic elsewhere instead?
        result = []
        lines = self.converted.splitlines()
        for idx, line in enumerate(lines):
            if line == '' and lines[idx-1].endswith('}'):
                continue
            result.append(line)
        return '\n'.join(result) + '\n'

    def write(self, *a, **kw):
        print(str(self))
        if a or kw:
            with open(*a, **kw) as f:
                f.write(str(self) + '\n')


def convert(block_type, block_names, *args, **kwargs):
    block = block_type
    for n in block_names:
        block += ' "%s"' % n
    block += ' {'
    if not args and not kwargs:
        return block + '}'

    # named args first
    block += recurse(kwargs)

    # then nested blocks
    for a in args:
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


def recurse(val, level=1):
    content = ''
    indent = ' ' * level * 2
    for k, v in val.items():
        if isinstance(v, list):
            content += '\n%s%s = [' % (indent, k)
            for x in v:
                content += '\n%s%s,' % (indent * 2, format(x))
            content += '\n%s]' % indent
        elif isinstance(v, dict):
            content += '\n%s%s = {' % (indent, k)
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
    if isinstance(val, Block):  # TODO: is this terraform-specific?
        return repr(val)
    elif isinstance(val, str):
        return '"%s"' % val
    elif isinstance(val, bool):
        return 'true' if val else 'false'
    return val
