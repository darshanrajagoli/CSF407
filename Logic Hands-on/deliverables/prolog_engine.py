"""
A minimal Prolog interpreter -- enough to execute the .pl files in this folder.

Why this file exists
--------------------
SWI-Prolog is not installed on the machine used for this laboratory, and the
handout allows "a locally installed version or an online environment".  Rather
than paste in output that was never produced, the Prolog programs are executed
by this small SLD-resolution engine, written from scratch, so every answer in
`prolog_session.txt` is a real answer computed from the real `.pl` files.

`planner.pl` and `reasoning.pl` are ordinary standard Prolog and load unchanged
in SWI-Prolog or SWISH; nothing here is a private dialect.

What is supported
-----------------
  * definite clauses:  head.   and   head :- g1, g2, ... .
  * atoms, variables, integers, compound terms, list syntax [a,b|T]
  * unification, backtracking, depth-first SLD resolution in clause order
  * builtins: true/0, fail/0, =/2, \\+/1 (negation as failure)
  * % line comments

That is exactly the "Facts + Rules + Inference" fragment the laboratory is
about.  Cut, arithmetic, assert/retract and I/O are deliberately absent.

Run:  python prolog_engine.py          (executes the lab's query script)
"""

import itertools
import re
import sys

# ---------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------

_counter = itertools.count(1)


class Var:
    __slots__ = ("name", "id")

    def __init__(self, name, vid=None):
        self.name = name
        self.id = vid if vid is not None else next(_counter)

    def __repr__(self):
        return "_%s%d" % (self.name, self.id)

    def __eq__(self, other):
        return isinstance(other, Var) and other.id == self.id

    def __hash__(self):
        return hash(("Var", self.id))


class Struct:
    """Compound term; an atom is a Struct with no arguments."""

    __slots__ = ("name", "args")

    def __init__(self, name, args=()):
        self.name = name
        self.args = tuple(args)

    @property
    def arity(self):
        return len(self.args)

    @property
    def indicator(self):
        return "%s/%d" % (self.name, self.arity)

    def __repr__(self):
        return format_term(self)

    def __eq__(self, other):
        return (isinstance(other, Struct) and other.name == self.name
                and other.args == self.args)

    def __hash__(self):
        return hash(("Struct", self.name, self.args))


NIL = Struct("[]")


def atom(name):
    return Struct(name)


def make_list(items, tail=NIL):
    out = tail
    for item in reversed(items):
        out = Struct(".", (item, out))
    return out


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

TOKEN_RE = re.compile(r"""
      (?P<ws>\s+)
    | (?P<comment>%[^\n]*)
    | (?P<neck>:-)
    | (?P<naf>\\\+)
    | (?P<punct>[()\[\],.|]|=)
    | (?P<num>-?\d+)
    | (?P<var>[A-Z_][A-Za-z0-9_]*)
    | (?P<atom>[a-z][A-Za-z0-9_]*|'[^']*')
""", re.VERBOSE)


def tokenize(text):
    tokens, pos = [], 0
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError("cannot tokenize at: %r" % text[pos:pos + 30])
        pos = m.end()
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        value = m.group()
        if kind == "atom" and value.startswith("'"):
            value = value[1:-1]
        tokens.append((kind, value))
    tokens.append(("eof", None))
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.scope = {}          # variable name -> Var, per clause

    def peek(self):
        return self.tokens[self.i]

    def next(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def expect(self, value):
        kind, got = self.next()
        if got != value:
            raise SyntaxError("expected %r, found %r" % (value, got))

    # -- terms ---------------------------------------------------------------

    def parse_term(self):
        kind, value = self.next()
        if kind == "num":
            return Struct(value)
        if kind == "var":
            if value == "_":
                return Var("_")
            if value not in self.scope:
                self.scope[value] = Var(value)
            return self.scope[value]
        if kind == "punct" and value == "[":
            return self.parse_list()
        if kind == "punct" and value == "(":
            term = self.parse_term()
            self.expect(")")
            return term
        if kind == "atom":
            if self.peek() == ("punct", "("):
                self.next()
                args = [self.parse_term()]
                while self.peek() == ("punct", ","):
                    self.next()
                    args.append(self.parse_term())
                self.expect(")")
                return Struct(value, args)
            return Struct(value)
        raise SyntaxError("unexpected token %r" % (value,))

    def parse_list(self):
        if self.peek() == ("punct", "]"):
            self.next()
            return NIL
        items = [self.parse_term()]
        while self.peek() == ("punct", ","):
            self.next()
            items.append(self.parse_term())
        tail = NIL
        if self.peek() == ("punct", "|"):
            self.next()
            tail = self.parse_term()
        self.expect("]")
        return make_list(items, tail)

    # -- goals ---------------------------------------------------------------

    def parse_goal(self):
        if self.peek() == ("naf", "\\+"):
            self.next()
            return Struct("\\+", [self.parse_goal()])
        left = self.parse_term()
        if self.peek() == ("punct", "="):
            self.next()
            right = self.parse_term()
            return Struct("=", [left, right])
        return left

    def parse_body(self):
        goals = [self.parse_goal()]
        while self.peek() == ("punct", ","):
            self.next()
            goals.append(self.parse_goal())
        return goals

    # -- clauses -------------------------------------------------------------

    def parse_clause(self):
        self.scope = {}
        head = self.parse_term()
        if self.peek() == ("neck", ":-"):
            self.next()
            body = self.parse_body()
        else:
            body = []
        self.expect(".")
        return (head, body)

    def parse_program(self):
        clauses = []
        while self.peek()[0] != "eof":
            clauses.append(self.parse_clause())
        return clauses

    def parse_query(self):
        self.scope = {}
        goals = self.parse_body()
        if self.peek() == ("punct", "."):
            self.next()
        return goals, dict(self.scope)


# ---------------------------------------------------------------------------
# Unification and resolution
# ---------------------------------------------------------------------------


def deref(term, bindings):
    while isinstance(term, Var) and term in bindings:
        term = bindings[term]
    return term


def unify(a, b, bindings):
    """Return an extended binding dict, or None."""
    a, b = deref(a, bindings), deref(b, bindings)
    if isinstance(a, Var):
        if a == b:
            return bindings
        out = dict(bindings)
        out[a] = b
        return out
    if isinstance(b, Var):
        out = dict(bindings)
        out[b] = a
        return out
    if a.name != b.name or a.arity != b.arity:
        return None
    for x, y in zip(a.args, b.args):
        bindings = unify(x, y, bindings)
        if bindings is None:
            return None
    return bindings


def rename(term, mapping):
    if isinstance(term, Var):
        if term not in mapping:
            mapping[term] = Var(term.name)
        return mapping[term]
    if not term.args:
        return term
    return Struct(term.name, [rename(a, mapping) for a in term.args])


class Database:
    def __init__(self, clauses=()):
        self.clauses = list(clauses)

    @classmethod
    def consult(cls, path):
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        return cls(Parser(tokenize(text)).parse_program())

    def matching(self, goal):
        for head, body in self.clauses:
            if head.name == goal.name and head.arity == goal.arity:
                yield head, body


MAX_DEPTH = 300


def solve(goals, bindings, db, depth=0):
    """Depth-first SLD resolution.  Yields a binding dict per solution."""
    if not goals:
        yield bindings
        return
    if depth > MAX_DEPTH:
        raise RecursionError("SLD resolution exceeded depth %d" % MAX_DEPTH)

    goal, rest = deref(goals[0], bindings), goals[1:]

    # -- builtins ------------------------------------------------------------
    if goal.name == "true" and goal.arity == 0:
        yield from solve(rest, bindings, db, depth + 1)
        return
    if goal.name in ("fail", "false") and goal.arity == 0:
        return
    if goal.name == "=" and goal.arity == 2:
        b2 = unify(goal.args[0], goal.args[1], bindings)
        if b2 is not None:
            yield from solve(rest, b2, db, depth + 1)
        return
    if goal.name == "\\+" and goal.arity == 1:
        # negation as failure -- the closed-world assumption, made executable
        for _ in solve([goal.args[0]], bindings, db, depth + 1):
            return
        yield from solve(rest, bindings, db, depth + 1)
        return

    # -- user clauses --------------------------------------------------------
    for head, body in db.matching(goal):
        mapping = {}
        head_r = rename(head, mapping)
        body_r = [rename(g, mapping) for g in body]
        b2 = unify(goal, head_r, bindings)
        if b2 is None:
            continue
        yield from solve(body_r + rest, b2, db, depth + 1)


# ---------------------------------------------------------------------------
# Query interface
# ---------------------------------------------------------------------------


def format_term(term, bindings=None):
    if bindings:
        term = deref(term, bindings)
    if isinstance(term, Var):
        return "_G%d" % term.id
    if term == NIL:
        return "[]"
    if term.name == "." and term.arity == 2:
        items, tail = [], term
        while isinstance(tail, Struct) and tail.name == "." and tail.arity == 2:
            items.append(format_term(tail.args[0], bindings))
            tail = deref(tail.args[1], bindings) if bindings else tail.args[1]
        suffix = "" if tail == NIL else "|" + format_term(tail, bindings)
        return "[" + ",".join(items) + suffix + "]"
    if not term.args:
        return term.name
    return "%s(%s)" % (term.name,
                       ",".join(format_term(a, bindings) for a in term.args))


def query(db, text, max_solutions=10):
    """Run a query string.  Returns (succeeded, list_of_binding_strings)."""
    goals, scope = Parser(tokenize(text)).parse_query()
    answers = []
    for bindings in solve(goals, {}, db):
        if scope:
            answers.append(", ".join(
                "%s = %s" % (name, format_term(var, bindings))
                for name, var in sorted(scope.items())))
        else:
            answers.append("")
        if len(answers) >= max_solutions:
            break
    return (len(answers) > 0), answers


def ask(db, text, expect=None, note=None, max_solutions=10):
    """Print a query the way a Prolog top level would, and return the result."""
    ok, answers = query(db, text, max_solutions)
    print("?- %s" % text)
    if not ok:
        print("false.")
    elif answers == [""] or all(a == "" for a in answers):
        print("true.")
    else:
        for a in answers:
            print("%s ." % a)
    if expect is not None:
        verdict = "as expected" if ok == expect else "*** UNEXPECTED ***"
        print("   [expected %s -- %s]" % (expect, verdict))
    if note:
        print("   %s" % note)
    print("")
    return ok
