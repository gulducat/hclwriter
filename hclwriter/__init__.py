import logging
logger = logging.getLogger(__name__)


class HCLDocument:
    def __init__(self):
        self.blocks = []

    def add(self, block):
        self.blocks.append(block)

    def write(self, filename=None):
        if filename:
            with open(filename, 'w') as f:
                for block in self.blocks:
                    logger.info(str(block))
                    f.write(str(block) + '\n')
        else:
            for block in self.blocks:
                print(block)


class Block:
    def __init__(self, block):
        self._block = block
        self._attrs = []
        self._args = ()
        self._kwargs = {}
        self._after_call_attrs = []
        self._called = False

    def __getattr__(self, attr):
        if self._called:
            # these are for referencing blocks in other blocks.
            self._after_call_attrs.append(attr)
        else:
            # this builds the actual content of the block
            self._attrs.append(attr)
        return self

    __getitem__ = __getattr__

    def __call__(self, *a, **kw):  # TODO: arguments? parameters?
        self._args = a
        self._kwargs = kw
        self._called = True
        return self

    # def _map(self, *a, **kw):
    #     def run():
    #         return a, kw
    #     return run

    @property
    def _mapped(self):
        mapped = {self._block: {
            # ".".join(self._attrs): self._kwargs
            ".".join(self._attrs): dict(a=self._args, kw=self._kwargs)
            # ".".join(self._attrs): (self._args, self._kwargs)
        }}
        logger.debug("mapped: %s" % mapped)
        return mapped

    @property
    def _hclwriter(self):
        return HCLWriter(self._mapped)

    def __str__(self):
        return self._hclwriter.string

    def __repr__(self):
        # TODO: without being terraform, this makes a lot less sense?
        # TODO: and loses self._block (and others attrs?)
        return ".".join(self._attrs + self._after_call_attrs)

    def _write(self, *a, **kw):
        self._hclwriter._write(*a, **kw)


class TerraformBlock(Block):
    def __repr__(self):
        if self._block == "provider":
            bits = self._attrs + [self._kwargs["alias"]]
        elif self._block in ["data", "module"]:
            bits = [self._block] + self._attrs + self._after_call_attrs
        else:
            bits = self._attrs + self._after_call_attrs
        return ".".join(bits)


class HCLWriter:
    def __init__(self, data):
        # funny dance to remove extraneous newlines.
        # placed here instead of elsewhere, because it has full context
        # of the entire string representation.
        stringed = convert(data)
        lines = stringed.splitlines()
        result = []
        for idx, line in enumerate(lines):
            if line == '' and lines[idx-1].endswith('}'):
                continue
            result.append(line)
        self.string = '\n'.join(result) + '\n'

    def __str__(self):
        return self.string

    def _write(self, *a, **kw):
        with open(*a, **kw) as f:
            logger.info(str(self))
            f.write(str(self) + '\n')


def convert(data):
    blocks = {}
    for b, vals in data.items():
        name = list(vals.keys())[0]
        blocks[b] = b
        if len(name) > 0:
            for x in name.split('.'):
                blocks[b] += ' "%s"' % x
        blocks[b] += ' {'

        data = vals[name]

        # TODO: move this tf/block-knowing stuff into Block class,
        #       or just give up on direct dict->hcl translation?
        # named parameters
        # TODO: KeyError 'kw' from stuff.py
        blocks[b] += recurse(data['kw'])
        # blocks
        # TODO: move nested indentation logic elsewhere
        for a in data['a']:
            block = '\n\n'
            for line in str(a).splitlines():
                if line == '':
                    block += '\n'
                else:
                    block += '  %s\n' % line
            blocks[b] += block

    blocks[b] += '\n}\n'
    return '\n'.join(blocks.values())


def recurse(val, level=1):
    content = ''
    indent = ' ' * level * 2
    for k, v in val.items():
        # if isinstance(v, tuple):
        #     for x in v:
        #         print(f"HELLO I AM TUPLE: {v} -- {x}")
        #         content += "\n%s%s {" % (indent, k)
        #         content += recurse(x, level=level + 1)
        #         content += "\n%s}" % indent
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
    if isinstance(val, Block):  # TODO: is this terraform-specific?
        return repr(val)
    elif isinstance(val, str):
        return '"%s"' % val
    elif isinstance(val, bool):
        return 'true' if val else 'false'
    return val
