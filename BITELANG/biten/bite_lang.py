from lark import Lark, Transformer, v_args

bite_grammar = r"""
    ?start: stmt*
    ?stmt: assign_stmt
         | print_stmt
         | func_def
         | func_call ";"
         | return_stmt
         | expr ";"
    assign_stmt: "let" NAME "=" expr ";"
    print_stmt: "println" "(" expr ")" ";"
    func_def: "fn" NAME "(" [params] ")" block
    params: NAME ("," NAME)*
    func_call: NAME "(" [args] ")"
    args: expr ("," expr)*
    return_stmt: "return" expr ";"
    block:  "{" stmt* "}"
    ?expr: INT      -> int
         | STRING   -> string
         | NAME     -> var
         | func_call
         | "(" expr ")"
         | expr "+" expr   -> add
         | expr "-" expr   -> sub
         | expr "*" expr   -> mul
         | expr "/" expr   -> div
    %import common.CNAME -> NAME
    %import common.INT
    %import common.WS
    %import common.ESCAPED_STRING -> STRING
    %ignore WS
"""

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Env(dict):
    def __init__(self, parent=None):
        self.parent = parent
    def __getitem__(self, k):
        if k in self:
            return super().__getitem__(k)
        elif self.parent:
            return self.parent[k]
        else:
            raise NameError(f"Variable '{k}' not found")
    def __setitem__(self, k, v):
        super().__setitem__(k, v)
    def copy(self):
        return Env(self)

@v_args(inline=True)
class BITETransformer(Transformer):
    def __init__(self):
        self.global_env = Env()
        self.functions = {}

    def assign_stmt(self, name, value):
        self.global_env[name] = value

    def print_stmt(self, value):
        print(value)

    def int(self, val):
        return int(val)

    def string(self, s):
        return s[1:-1]  # strip quotes

    def var(self, name):
        return self.global_env[name]

    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a // b

    def func_def(self, name, params, block):
        pname = str(name)
        self.functions[pname] = (params or [], block)

    def params(self, *args): return list(args)
    def args(self, *args): return list(args)

    def func_call(self, name, args=None):
        fname = str(name)
        if fname == 'println':
            print(*(args or []))
            return None
        if fname not in self.functions:
            raise Exception(f"Function '{fname}' not defined")
        param_names, block = self.functions[fname]
        call_env = Env(self.global_env)
        for p, a in zip(param_names, args or []):
            call_env[p] = a
        try:
            self.exec_block(block, call_env)
        except ReturnValue as rv:
            return rv.value

    def block(self, *stmts):
        return list(stmts)

    def return_stmt(self, value):
        raise ReturnValue(value)

    def expr(self, val): return val
    def stmt(self, val): return val

    def start(self, *stmts):
        for s in stmts:
            if s is not None:
                pass

    def exec_block(self, block, env):
        old_env = self.global_env
        self.global_env = env
        for stmt in block:
            if stmt is not None:
                pass
        self.global_env = old_env

def run_bite_code(code):
    parser = Lark(bite_grammar, parser='lalr', transformer=BITETransformer())
    parser.parse(code)