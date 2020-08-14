#!/usr/bin/env python

from hclwriter import file
from hclwriter.terraform import TerraformBlock as TF

f = file.start()


def provider(r):
    return TF('provider').aws(alias=r, region=r)


module_kw = {
    'source': './my-module',
    'providers': {'aws': provider('us-east-1')},
}

one = TF('module').one(
    arg='fancy one',
    **module_kw
)

two = TF('module').two(
    arg='fancy two',
    **module_kw
)

TF('output').ids(
    value={
        'one': one.id,
        'two': two.id,
    }
)

f.end()
