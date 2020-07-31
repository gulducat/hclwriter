import logging
from typing import Iterable

from hclwriter import Block

logger = logging.getLogger(__name__)


class HCLFile:
    _filename = None

    def __init__(self,
                 *blocks: Iterable[Block],
                 filename: str = None,
                 mode: str = 'w'):
        self._blocks = [b for b in blocks]
        if filename:
            self._filename = filename
        self._mode = mode

    @property
    def num_blocks(self):
        return len(self._blocks)

    def add(self, *blocks: Iterable[Block]):
        for block in blocks:
            self._blocks.append(block)
        return self

    __iadd__ = add  # +=

    def write(self, *blocks, filename=None, mode='w'):
        self.add(*blocks)

        # note: class/instance attributes go in alphabetical order
        self.add(*[
            getattr(self, i)
            for i in dir(self)
            if isinstance(getattr(self, i), Block)
            and not i.startswith('_')
        ])

        fn = filename if filename else self._filename
        mode = mode if mode else self._mode

        joined_blocks = '\n'.join([
            str(b) for b in self._blocks
        ])

        if fn:
            with open(fn, mode) as f:
                logger.info(joined_blocks)
                f.write(joined_blocks + '\n')
        else:
            print(joined_blocks)  # TODO: cov missing ...

        # return joined_blocks  # TODO: something like this...
        return self
