from pyparsing import Word, alphas, alphanums, ZeroOrMore, OneOrMore, Group, Literal, Forward, Suppress, Optional


class ValuesLine:
    transforms = {
        'int': int,
        'float': float,
        'str': str
    }

    def __init__(self, names):
        self.names = names.asList()

    def __repr__(self):
        return f"VL({', '.join(map(str, self.names))})"
    
    def parse(self, lines, d):
        line = lines.pop(0).split(' ')
        for name, val in zip(self.names, line):
            op = int if len(name) == 1 else self.transforms.get(name[1], int)
            d[name[0]] = op(val)


class MultLine:
    def __init__(self, tokens):
        tokens = tokens.asList()
        self.name = tokens[0]
        self.mult_var = tokens[1]
        self.lines = tokens[2:]
    
    def __repr__(self):
        return f'{self.mult_var} * {self.lines}'
    
    def parse(self, lines, d):
        repetitions_nb = d[self.mult_var]
        d[self.name] = [inst.parse(lines, d) for inst in self.lines
                        for _ in range(repetitions_nb)]


class Instructions:
    def __init__(self, tokens):
        self.instructions = tokens.asList()
    
    def __repr__(self):
        return str(self.instructions)
    
    def parse(self, lines, values=None):
        values = {}
        for inst in self.instructions:
            inst.parse(lines, values)
        return values


name = Word(alphanums + '_')
times = Suppress(Literal('*'))
lbr = Suppress(Literal('['))
rbr = Suppress(Literal(']'))
col = Suppress(Literal(':'))
scol = Suppress(Literal(';'))
qm = Suppress(Literal('?'))

single_vl = OneOrMore(Group(name + Optional(qm + name))) + scol
multiple_vl = OneOrMore(single_vl)

repeated_struct = Forward()
rs_core = multiple_vl + ZeroOrMore(multiple_vl | repeated_struct)
repeated_struct << name + col + name + times + \
                    lbr + rs_core + rbr

single_vl.setParseAction(ValuesLine)
rs_core.setParseAction(Instructions)
repeated_struct.setParseAction(MultLine)


def parse_from_grammar(data_filename, grammar_filename):
    with open(data_filename) as f:
        lines = [line.rstrip('\n') for line in f]
    parser = rs_core.parseFile(grammar_filename)[0]
    return parser.parse(lines)
