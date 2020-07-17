#!/usr/bin/env python

import json
from hclwriter import HCLWriter

with open("test.json") as f:
    data = json.load(f)

h = HCLWriter(data)
h._write("test.hcl")
