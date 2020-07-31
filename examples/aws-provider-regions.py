#!/usr/bin/env python

# from sys import path
# path.insert(0, '/Users/danielbennett/git/gulducat/pyhclwriter')
from hclwriter.file import HCLFile
from hclwriter.terraform import TerraformBlock as TF


REGIONS = ['us-east-1', 'us-west-2']  # could get all with boto3

# main = HCLFile()
# for r in REGIONS:
#     p = TF('provider').aws(
#         alias=r,
#         region=r,
#     )
#     main += p
#     m = TF('module')[f'cool-{r}'](
#         provider=p,
#         region=r,
#     )
#     main += m

# main.write()


def one():
    for r in REGIONS:
        class MyFile(HCLFile):
            # these are written out in alphabetical order, hence "a_" and "b_"
            # for sensible order in the resulting terraform
            a_provider = TF('provider').aws(
                alias=r,
                region=r,
            )
            b_module = TF('module')[f'cool-{r}'](
                source='./modules/cool',
                provider=a_provider,
            )
        MyFile().write()

one()