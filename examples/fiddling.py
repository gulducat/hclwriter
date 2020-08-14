#!/usr/bin/env python

from functools import partial

from hclwriter import file
from hclwriter.file import HCLFile
from hclwriter.terraform import TerraformBlock as TF

f = file.start()

r = 'us-east-1'


def silly_shit():
    p = TF('provider').aws(alias=r, region=r)
    m = partial(TF('module')[r], source='./my-module')
    m(providers={'aws': p})
    m(providers={'aws': p})  # ignored becuase identical to previous
    m(providers={'aws': p.ok})  # makes a second, actually identical one


# silly_shit()
TF('comment')(msg='ok hello')
f.write()
