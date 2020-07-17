#!/usr/bin/env python
import json
from hclwriter import convert

with open("test.json") as f:
    data = json.load(f)

print(convert(data))
