class HCLer(object):
    def __init__(self, data):
        self.data = data
        self.sections = {}
        self.parse()

    def __str__(self):
        return '\n'.join(self.sections.values())

    def write(self, filename):
        with open(filename, "w") as f:
            f.write(str(self))

    def parse(self):
        for s, vals in self.data.items():
            sname = list(vals.keys())[0]
            self.sections[s] = '%s "%s" {' % (s, sname)
            self.sections[s] += self.recurse(vals[sname])
            self.sections[s] += '\n}\n'

    def recurse(self, val, level=1):
        content = ''
        indent = ' ' * level * 2
        for k, v in val.items():
            if isinstance(v, list):
                content += '\n%s%s = [' % (indent, k)
                for x in v:
                    content += '\n%s%s,' % (indent * 2, self.format(x))
                content += '\n%s]' % indent
            elif isinstance(v, dict):
                content += '\n%s%s = {' % (indent, k)
                content += self.recurse(v, level=level + 1)
                content += '\n%s}' % indent
            else:
                content += '\n%s%s = %s' % (indent, k, self.format(v))
        return content

    def format(self, val):
        if isinstance(val, str):
            return '"%s"' % val
        elif isinstance(val, bool):
            return "true" if val else "false"
        return val
