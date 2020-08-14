#!/usr/bin/env python

from textwrap import dedent

from hclwriter import file
from hclwriter.terraform import TerraformBlock as TF


def types():
    f = file.start()
    # region = TF('variable').region.ok(  # TODO: validate?? see terraform.py
    variables = {
        'region': TF('variable').region(
            description='region name',
            default='us-east-1',
            # things wrapped in TF() are written verbatim
            type=TF('string'),
        ),
        'count': TF('variable').num_things(
            description='how many',
            default=1,
            type=TF('number'),
        ),
        'daters': TF('variable').mappy(
            description='fancy data',
            default={"names": ["me", "you"]},
            type=TF('map(list(string))'),
        )
    }
    data = TF('data').cool.info(**variables)
    TF('resource').cool.thing(id=data.id, **variables)
    f.write()

    # writes:
    return dedent('''\
      variable "region" {
        description = "region name"
        default = "us-east-1"
        type = string
      }

      variable "num_things" {
        description = "how many"
        default = 1
        type = number
      }

      variable "mappy" {
        description = "fancy data"
        default = {
          names = [
              "me",  # TODO: indentation here
              "you",
          ]
        }
        type = map(list(string))
      }

      module "cool_thing" {
        region = var.region
        count = var.num_things
        daters = var.mappy
      }

      module "another_thing" {
        region = var.region
        count = var.num_things
        daters = var.mappy
      }
    ''')


types()
