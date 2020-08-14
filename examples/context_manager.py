#!/usr/bin/env python

from textwrap import dedent

from hclwriter.file import HCLFile
from hclwriter.terraform import TerraformBlock as TF


def context_manager():
    # HCLFile magically discovers each TF `Block` that gets called
    with HCLFile():
        r = 'us-east-1'
        TF('module').mine(
            source='./my-module',
            providers={'aws': TF('provider').aws(alias=r, region=r)},
        )

    # writes:
    return dedent('''\
      provider "aws" {
        alias = "us-east-1"
        region = "us-east-1"
      }

      module "mine" {
        source = "./my-module"
        providers = {
          aws = aws.us-east-1
        }
        region = var.region
      }
    ''')


context_manager()




# TODO: gracefully remove providers...  multi-pass

# TODO: amanda's review: "so you're a tech genius", "so, you're keeping the peons dumb"
