#!/usr/bin/env python

import json
import hcl  # pip install pyhcl

from hclwriter import HCLWriter

# json source
with open("stuff.json") as f:
    stuff = json.load(f)
h = HCLWriter(stuff)
print(h)

# hcl source
with open("in.hcl") as f:
    data = hcl.load(f)

data["path"]["auth/*"]["capabilities"].append("fancy")
h = HCLWriter(data)
print(h)
h._write("out.hcl")
