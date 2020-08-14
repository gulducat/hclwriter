import logging
from typing import List, Tuple

from hclwriter import Block

logger = logging.getLogger(__name__)


def start(*a, **kw):
    return HCLFile(*a, **kw).__enter__()


class HCLFile:
    _filename = None

    def __init__(self, filename: str = None, mode: str = 'w'):
        if filename:
            self._filename = filename
        self._mode = mode
        self._blocks = []

    def add(self, *blocks: Tuple[Block]) -> 'HCLFile':
        for block in blocks:
            if block not in self._blocks:
                self._blocks.append(block)
        return self

    __iadd__ = add  # +=

    def __str__(self) -> str:
        return '\n'.join([
            str(b) for b in self.blocks
        ])

    @property
    def blocks(self) -> List[Block]:
        # note: class/instance attributes go in alphabetical order
        cls_blocks = []
        for attr in dir(self):  # TODO: self.__dict__ doesn't get class attributes...
            if attr == 'blocks' or attr.startswith('_'):
                continue
            val = getattr(self, attr)
            if val in self._blocks or not isinstance(val, Block):
                continue
            cls_blocks.append(val)

        return self._blocks + cls_blocks

    def write(self, filename: str = None, mode: str = 'w'):
        fn = filename if filename else self._filename
        mode = mode if mode else self._mode

        string = str(self)

        if fn:
            with open(fn, mode) as f:
                logger.info(string)
                # if mode == 'a':
                #     string = '\n' + string
                f.write(string)
        else:
            print(string)  # TODO: cov missing ...

    def __enter__(self):
        # we only want `Block`s defined within the context manager
        self._blocks_copy = Block._instances[:]
        Block._instances = []
        self._blocks = Block._instances
        return self

    def __exit__(self, *ok):
        self.write()
        Block._instances = self._blocks_copy[:]

    end = __exit__
