#!/usr/bin/env python

import json
import hcl  # pip install pyhcl

from hcler import HCLer

# json source
with open("stuff.json") as f:
    stuff = json.load(f)
h = HCLer(stuff)
print(h)

# hcl source
with open("in.hcl") as f:
    data = hcl.load(f)

data["path"]["auth/*"]["capabilities"].append("fancy")
h = HCLer(data)
print(h)
h.write("out.hcl")
