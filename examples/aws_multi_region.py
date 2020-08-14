#!/usr/bin/env python

from os import remove
from textwrap import dedent
from unittest import TestCase

from hclwriter.file import HCLFile
from hclwriter.terraform import TerraformBlock as TF

TF_FILE = 'aws_multi_region.tf'
REGIONS = ['us-east-1', 'us-west-2']  # could get all using boto3


def straight_forward():

    tf = HCLFile(TF_FILE)
    for r in REGIONS:
        p = TF('provider').aws(
            alias=r,
            region=r,
        )
        m = TF('module')[f'stuff-{r}'](
            source='./my-module',
            providers={'aws': p},
        )
        tf += p
        tf += m
    tf.write()

    # writes:
    return dedent('''\
      provider "aws" {
        alias = "us-east-1"
        region = "us-east-1"
      }

      module "stuff-us-east-1" {
        source = "./my-module"
        providers = {
          aws = aws.us-east-1
        }
      }

      provider "aws" {
        alias = "us-west-2"
        region = "us-west-2"
      }

      module "stuff-us-west-2" {
        source = "./my-module"
        providers = {
          aws = aws.us-west-2
        }
      }
    ''')


def some_python_flavor():

    tf = HCLFile(TF_FILE)
    providers = {
      r: TF('provider').aws(alias=r, region=r)
      for r in REGIONS
    }
    modules = [
      TF('module')[f'stuff-{r}'](
        source='./my-module',
        providers={'aws': p},
      )
      for r, p in providers.items()
    ]
    tf.add(*providers.values())
    tf.add(*modules)
    tf.write()

    # writes:
    return dedent('''\
      provider "aws" {
        alias = "us-east-1"
        region = "us-east-1"
      }

      provider "aws" {
        alias = "us-west-2"
        region = "us-west-2"
      }

      module "stuff-us-east-1" {
        source = "./my-module"
        providers = {
          aws = aws.us-east-1
        }
      }

      module "stuff-us-west-2" {
        source = "./my-module"
        providers = {
          aws = aws.us-west-2
        }
      }
    ''')


def classy():

    # this one is a bit silly, but gets some ideas across.
    for r in REGIONS:
        class MyFile(HCLFile):
            _filename = TF_FILE
            # will be written in alphabetical order per region by variable name
            # 'm'odule before 'p'rovider
            p = TF('provider').aws(
                alias=r,
                region=r,
            )
            m = TF('module')[f'stuff-{r}'](
                source='./my-module',
                providers={'aws': p},
            )
        MyFile().write(mode='a')  # 'a' = append to file

    # writes:
    return dedent('''\
      module "stuff-us-east-1" {
        source = "./my-module"
        providers = {
          aws = aws.us-east-1
        }
      }

      provider "aws" {
        alias = "us-east-1"
        region = "us-east-1"
      }
      module "stuff-us-west-2" {
        source = "./my-module"
        providers = {
          aws = aws.us-west-2
        }
      }

      provider "aws" {
        alias = "us-west-2"
        region = "us-west-2"
      }
    ''')


class TestStyles(TestCase):
    def set_up(self):
        remove(TF_FILE)

    def assert_written(self, expect):
        with open(TF_FILE) as tf:
            self.assertEqual(expect, tf.read())
        remove(TF_FILE)

    def test_straight_forward(self):
        expect = straight_forward()
        self.assert_written(expect)

    def test_some_python_flavor(self):
        expect = some_python_flavor()
        self.assert_written(expect)

    def test_classy(self):
        expect = classy()
        self.assert_written(expect)
