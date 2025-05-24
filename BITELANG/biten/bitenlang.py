from lark import Lark, Transformer, v_args

biten_grammar = r"""
    ?start: stmt*
    ?stmt: cloudvarassign
         | cloudprintstmt
         | cloudfunctiondef
         | cloudfunctioncall ";"
         | cloudreturnstmt
         | exprstmt
    cloudvarassign: "cloudvar" NAME "=" expr ";"
    cloudprintstmt: "cloudprint" "(" expr ")" ";"
    cloudfunctiondef: "cloudfunction" NAME "(" [paramlist] ")" cloudblock
    paramlist: NAME ("," NAME)*
    cloudfunctioncall: NAME "(" [arglist] ")"
    arglist: expr ("," expr)*
    cloudreturnstmt: "cloudreturn" expr ";"
    cloudblock:  "{" stmt* "}"
    exprstmt: expr ";"
    ?expr: INT      -> int
         | NAME     -> var
         | cloudfunctioncall
         | "(" expr ")"
         | expr "+" expr   -> add
         | expr "-" expr   -> sub
         | expr "*" expr   -> mul
         | expr "/" expr   -> div
    %import common.CNAME -> NAME
    %import common.INT
    %import common.WS
    %ignore WS
"""

def _normalize_name(tok):
    return str(tok).lower()

class CloudReturn(Exception):
    def __init__(self, value):
        self.value = value

class CloudEnv(dict):
    def __init__(self, parent=None):
        self.parent = parent
    def __getitem__(self, k):
        k = k.lower()
        if k in self:
            return super().__getitem__(k)
        elif self.parent:
            return self.parent[k]
        else:
            raise NameError(f"CloudVar '{k}' not found")
    def __setitem__(self, k, v):
        super().__setitem__(k.lower(), v)
    def copy(self):
        return CloudEnv(self)

@v_args(inline=True)
class CloudTransformer(Transformer):
    def __init__(self, output_func=None):
        self.globalenv = CloudEnv()
        self.functions = {}
        self.output_func = output_func or print

    def cloudvarassign(self, name, value):
        self.globalenv[_normalize_name(name)] = value

    def cloudprintstmt(self, value):
        self.output_func(f"[CLOUDPRINT] {value}")

    def int(self, val):
        return int(val)

    def var(self, name):
        return self.globalenv[_normalize_name(name)]

    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a // b

    def cloudfunctiondef(self, name, params, block):
        pname = _normalize_name(name)
        self.functions[pname] = (params or [], block)

    def paramlist(self, *args): return list(map(_normalize_name, args))
    def arglist(self, *args): return list(args)

    def cloudfunctioncall(self, name, args=None):
        fname = _normalize_name(name)
        if fname not in self.functions:
            raise Exception(f"CloudFunction '{fname}' not defined")
        param_names, block = self.functions[fname]
        call_env = CloudEnv(self.globalenv)
        for p, a in zip(param_names, args or []):
            call_env[p] = a
        try:
            self.exec_block(block, call_env)
        except CloudReturn as cr:
            return cr.value

    def cloudblock(self, *stmts):
        return list(stmts)

    def cloudreturnstmt(self, value):
        raise CloudReturn(value)

    def exprstmt(self, val): return val
    def stmt(self, val): return val
    def start(self, *stmts): pass

    def exec_block(self, block, env):
        old_env = self.globalenv
        self.globalenv = env
        for stmt in block:
            pass
        self.globalenv = old_env

def run_biten_code(code, output_func=None):
    parser = Lark(biten_grammar, parser='lalr', transformer=CloudTransformer(output_func=output_func), maybe_placeholders=False)
    parser.parse(code)