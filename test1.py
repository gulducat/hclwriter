#!/usr/bin/env python

import logging

from hclwriter import HCLDocument
from hclwriter import TerraformBlock as TF

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    doc = HCLDocument()

    thing = TF("data").thing.name(ok="sure")
    dyn_statements = [
        TF("dynamic").statement(
            TF("nested")(ok='sure'),
            dyn_kw=f'some_dyn_kw_{x}',
        )
        for x in range(2)
    ]
    r = TF("resource").aws_iam_thing.cool(
        # *dyn_statements,
        res_kw="some_res_kw",
        thing=thing.some_key,
    )
    doc.add(r)

    doc.add(
        TF("resource").aws_thing.coolname(cool_arg="cool_value")
    )

    doc.write('test1.tf')
    # logger.info(r)
    # r._write('test1.tf', 'w')


main()
