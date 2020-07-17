#!/usr/bin/env python

from sys import exit

from hclwriter import TerraformBlock as TF

outfile = "tfgen.tf"

# providers = {}
# for name, stuffs in someconfig.items():
#     providers[name] = TF("provider").aws(**stuffs)

t = TF("output").tupley(value=(
    {'ok': {'yea': 'sure'}},
    {'ok': {'yea': 'another'}},
))
pro = TF("provisioner")["local-exec"](command="echo first") #.ok.yea(mmhm='sure')
t = TF("resource").null_resource.null(pro)
# # t = TF("resource").null_resource.null(provisioner=(
# #     {"local-exec": {"command": "echo first"}},
# #     {"local-exec": {"command": "echo second"}},
# # ))
t._write(outfile, "w")
# pro._write(outfile, "a")

# exit()

p1 = TF("provider").aws(alias="fancy", region="us-east-1")
r1 = TF("resource").aws_something.some_thing(var="value")
d1 = TF("data").aws_dater.tots(thingo=99.99)
m1 = TF("module").mymod(source="./moddo", providers={repr(p1): p1})
r2 = TF("resource").aws_another.another_thing(
    provider=p1,
    var=r1.some_output,
    daters=d1,
)
o = TF("output").some_out(value=m1.some_out)

p1._write(outfile, "a")
for _x in [r1, d1, r2, m1, o]:
    _x._write(outfile, "a")
# print("\n".join([
#     str(_x)
#     for _x in [p, r1, d1, r2, m]
# ]))

# these things may not work very well...
# Warning: Quoted type constraints are deprecated
v = TF("variable").somevar(default="yermom", type="string")
# print(v)
v._write(outfile, "a")
# THIS IS HARD AND MAYBE NOT HELPFUL.. JUST WRITE TERRAFORM
# rloop = TF("resource").aws_loopy.things(for_each="{for k, v in ok: k => v}")

# meh.  would need more complicated subprocess not to swallow errors
# print("+ terraform fmt")
# from subprocess import check_output, STDOUT
# print(check_output(["terraform", "fmt"], stderr=STDOUT, encoding="utf-8"))






exit()

accounts = [
    {"name": "one"},
    {"name": "two"},
    {"name": "three"},
]

providers = []
mods = []
for a in accounts:
    name = a["name"]
    p = TF("provider").aws(alias=f"account_{name}", region="us-east-1")
    providers.append(p)
    mods.append(
        getattr(TF("module"), f"account_{name}")(
            source="./moddymod",
            provider=p,
            name=name,
        )
    )

for block in providers + mods:
    print(block)

# # wipe teh files
# for f in ["zzz.providers.tf", "zzz.accounts.tf"]:
#     with open(f, "w"):
#         pass

# for p in providers:
#     p1._write("zzz.providers.tf", "a")

# for m in mods:
#     m1._write("zzz.accounts.tf", "a")
