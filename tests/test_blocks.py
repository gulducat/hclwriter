#!/usr/bin/env python

from textwrap import dedent
from unittest import TestCase

from hclwriter import Block
from hclwriter.terraform import TerraformBlock as TF


def assert_blocks(string, *blocks):
    result = ''
    for block in blocks:
        result += str(block)
    assert dedent(string) == result


class TestBlock(TestCase):
    def test_block_with_param(self):
        block = Block('block')(ok='sure')
        expect = '''\
        block {
          ok = "sure"
        }
        '''
        assert_blocks(expect, block)

    def test_named_block(self):
        block = Block('block').named(ok='sure')
        expect = '''\
        block "named" {
          ok = "sure"
        }
        '''
        assert_blocks(expect, block)

    def test_item_syntax(self):
        block = Block('block')['named'](ok='sure')
        expect = '''\
        block "named" {
          ok = "sure"
        }
        '''
        assert_blocks(expect, block)

    def test_double_named_block(self):
        block = Block('block').named.second(ok='sure')
        expect = '''\
        block "named" "second" {
          ok = "sure"
        }
        '''
        assert_blocks(expect, block)

    def test_nested_blocks(self):
        inner = Block('inner')(ok='sure')
        outer = Block('outer')(inner)
        expect = '''\
        outer {
          inner {
            ok = "sure"
          }
        }
        '''
        assert_blocks(expect, outer)

    def test_args_and_nested(self):
        inner = Block('inner')(ok='sure')
        outer = Block('outer')(inner, yea='tru')
        expect = '''\
        outer {
          yea = "tru"

          inner {
            ok = "sure"
          }
        }
        '''
        assert_blocks(expect, outer)

    def test_non_block_arg(self):
        with self.assertRaises(TypeError):
            Block('block')('not a block')

    def test_multiple_calls(self):
        block = Block('block')
        one = block(val='one')
        two = block(val='two')
        expect = '''\
        block {
          val = "one"
        }
        block {
          val = "two"
        }
        '''
        assert_blocks(expect, one, two)

    # value formatting

    def test_value_string(self):
        block = Block('block')(val='sure')
        expect = '''\
        block {
          val = "sure"
        }
        '''
        assert_blocks(expect, block)

    def test_value_bool_true(self):
        block = Block('block')(val=True)
        expect = '''\
        block {
          val = true
        }
        '''
        assert_blocks(expect, block)

    def test_value_bool_false(self):
        block = Block('block')(val=False)
        expect = '''\
        block {
          val = false
        }
        '''
        assert_blocks(expect, block)

    def test_value_int(self):
        block = Block('block')(val=1)
        expect = '''\
        block {
          val = 1
        }
        '''
        assert_blocks(expect, block)

    def test_value_float(self):
        block = Block('block')(val=1.1)
        expect = '''\
        block {
          val = 1.1
        }
        '''
        assert_blocks(expect, block)

    def test_value_list(self):
        block = Block('block')(val=['sure', 1, 1.1])
        expect = '''\
        block {
          val = [
            "sure",
            1,
            1.1,
          ]
        }
        '''
        assert_blocks(expect, block)

    def test_value_map(self):
        block = Block('block')(val={'ok': 1})
        expect = '''\
        block {
          val = {
            ok = 1
          }
        }
        '''
        assert_blocks(expect, block)

    def test_block_reference(self):
        inner = Block('inner').named(ok='sure')
        outer = Block('outer')(inner=inner)
        expect = '''\
        inner "named" {
          ok = "sure"
        }
        outer {
          inner = inner.named
        }
        '''
        assert_blocks(expect, inner, outer)

    def test_block_reference_multiple(self):
        inner = Block('inner').named(ok='sure')
        outer = Block('outer')(thing_id=inner.thing.id)
        # HACK:
        # another = Block('another')(id=TF('inner.named.id'))
        another = Block('another')(id=inner.id)
        expect = '''\
        inner "named" {
          ok = "sure"
        }
        outer {
          thing_id = inner.named.thing.id
        }
        another {
          id = inner.named.id
        }
        '''
        assert_blocks(expect, inner, outer, another)


class TestTerraformBlock(TestCase):

    def test_ref_variable(self):
        var = TF('variable').somevar()
        block = TF('block')(var=var)
        expect = '''\
        variable "somevar" {}
        block {
          var = var.somevar
        }
        '''
        assert_blocks(expect, var, block)

    def test_ref_local(self):
        lvars = TF('locals')(somelocal='someval')
        block = TF('block')(var=lvars.somelocal)
        expect = '''\
        locals {
          somelocal = "someval"
        }
        block {
          var = local.somelocal
        }
        '''
        assert_blocks(expect, lvars, block)

    def test_ref_provider(self):
        provider = TF('provider').aws(alias='fancy')
        resource = TF('resource').thing.name(provider=provider)
        expect = '''\
        provider "aws" {
          alias = "fancy"
        }
        resource "thing" "name" {
          provider = aws.fancy
        }
        '''
        assert_blocks(expect, provider, resource)

    def test_ref_resource(self):
        inner = TF('resource').fancy.thing(arg='val')
        outer = TF('resource').another.thing(fancy=inner)
        expect = '''\
        resource "fancy" "thing" {
          arg = "val"
        }
        resource "another" "thing" {
          fancy = fancy.thing
        }
        '''
        assert_blocks(expect, inner, outer)

    def test_ref_data_source(self):
        inner = TF('data').fancy.info(arg='val')
        outer = TF('resource').fancy.thing(daters=inner)
        expect = '''\
        data "fancy" "info" {
          arg = "val"
        }
        resource "fancy" "thing" {
          daters = data.fancy.info
        }
        '''
        assert_blocks(expect, inner, outer)

    def test_ref_provider_require_alias(self):
        p = TF('provider').aws()  # no alias
        r = TF('thing')(provider=p)
        with self.assertRaises(KeyError):
            str(r)

    def test_ref_module(self):
        # no "source" kw is ok, let Terraform itself handle that kind of error.
        m = TF('module').name()
        r = TF('resource').thing.name(somekey=m)
        expect = '''\
        module "name" {}
        resource "thing" "name" {
          somekey = module.name
        }
        '''
        assert_blocks(expect, m, r)
