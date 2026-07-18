"""GLSL AST -> Python kernel source.

Emits a `run_pixel(ctx, out)` function that calls the noisemaker_cpu.runtime
Runtime (ctx.rt), matching the runtime contract. Does its own GLSL type
inference (widths, int/uint/float base, matrices, arrays) to drive emission.
"""

from __future__ import annotations

import json

TYPE = {
    "void": {"base": "void", "width": 0},
    "bool": {"base": "bool", "width": 1},
    "int": {"base": "int", "width": 1},
    "uint": {"base": "uint", "width": 1},
    "float": {"base": "float", "width": 1},
    "vec2": {"base": "float", "width": 2},
    "vec3": {"base": "float", "width": 3},
    "vec4": {"base": "float", "width": 4},
    "ivec2": {"base": "int", "width": 2},
    "ivec3": {"base": "int", "width": 3},
    "ivec4": {"base": "int", "width": 4},
    "uvec2": {"base": "uint", "width": 2},
    "uvec3": {"base": "uint", "width": 3},
    "uvec4": {"base": "uint", "width": 4},
    "bvec2": {"base": "bool", "width": 2},
    "bvec3": {"base": "bool", "width": 3},
    "bvec4": {"base": "bool", "width": 4},
    "mat2": {"base": "float", "width": 4, "mat": 2},
    "mat3": {"base": "float", "width": 9, "mat": 3},
    "mat4": {"base": "float", "width": 16, "mat": 4},
    "sampler2D": {"base": "sampler", "width": 0},
    "sampler3D": {"base": "sampler", "width": 0},
    "samplerCube": {"base": "sampler", "width": 0},
    "sampler2DArray": {"base": "sampler", "width": 0},
}
FLOAT = TYPE["float"]
BOOL = TYPE["bool"]
VEC4 = TYPE["vec4"]

_SWZ = set("xyzwrgbastpq")


def base_of(t):
    return t["base"] if t and t.get("base") else "float"


def width_of(t):
    return t["width"] if t and t.get("width") else 1


def q(s):
    return json.dumps(str(s))


_RESERVED = {
    "and",
    "or",
    "not",
    "in",
    "is",
    "lambda",
    "class",
    "def",
    "return",
    "if",
    "else",
    "for",
    "while",
    "None",
    "True",
    "False",
    "global",
    "nonlocal",
    "import",
    "from",
    "as",
    "with",
    # emitted-kernel infrastructure names — a shader local named any of these
    # would shadow the runtime/globals holder and break the closure.
    "rt",
    "g",
    "U",
    "T",
    "ctx",
    "out",
    "run_pixel",
}


def py_ident(name):
    return f"_{name}" if name in _RESERVED else name


# Calls routed to the runtime instead of treated as user functions / component-wise.
def _construct_base(t):
    return f", base={q(t['base'])}" if t and t.get("base") in ("int", "uint") else ""


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def child(self):
        return Scope(self)

    def define(self, name, typ, pyname=None):
        entry = {"py": pyname or py_ident(name), "type": typ}
        self.vars[name] = entry
        return entry

    def resolve(self, name):
        s = self
        while s:
            if name in s.vars:
                return s.vars[name]
            s = s.parent
        return None


class CodeGen:
    def __init__(self, program, outputs, varyings):
        self.program = program
        self.outputs = outputs or ["fragColor"]
        self.varyings = set(varyings or [])
        self.root = Scope()
        self.overloads = {}  # base name -> [ {mangled, ptypes, ret, node} ]
        self.funcs = []
        self.uniforms = []  # {name, type}
        self.globals = []  # {name, type, init}
        self.structs = {}  # name -> [ (fieldtype, fieldname) ]
        self.loop_id = 0
        self.uses_deriv = False
        self.cur_out = []  # out/inout param pynames of the function being emitted

    # ---- collect ----
    def collect(self):
        for d in self.program["decls"]:
            if d["k"] == "struct":
                self.structs[d["name"]] = [(f[0], f[1]) for f in d["fields"]]
            elif d["k"] == "func":
                self._collect_func(d)
            elif d["k"] == "proto":
                pass
            elif d["k"] == "decl":
                self._collect_decl(d)
            elif d["k"] == "ubo":
                # Anonymous std140 block members are addressed like bare uniforms
                # (e.g. `data[i]`); each is bound as a uniform value.
                for m in d["members"]:
                    self.uniforms.append({"name": m["name"], "type": self.type_of_name(m["type"], m.get("array"))})

    def type_of_name(self, tname, array=None):
        t = dict(TYPE.get(tname, {"base": "float", "width": 1}))
        if tname in self.structs:
            t = {"base": "struct", "width": 0, "struct": tname}
        if array is not None:
            t = dict(t)
            t["array"] = True
        return t

    def _collect_func(self, d):
        ret = self.type_of_name(d["ret"])
        ptypes = [self.type_of_name(p[0]) for p in d["params"]]
        out_idxs = [
            i for i, p in enumerate(d["params"]) if len(p) > 2 and any(qu in ("out", "inout") for qu in (p[2] or []))
        ]
        mangled = py_ident(d["name"]) + "__" + ("_".join(_type_name(t) for t in ptypes) if ptypes else "void")
        entry = {"mangled": mangled, "ptypes": ptypes, "ret": ret, "node": d, "out_idxs": out_idxs}
        self.funcs.append(entry)
        self.overloads.setdefault(d["name"], []).append(entry)

    def _collect_decl(self, d):
        quals = d.get("quals", [])
        base_t = d["type"]
        if "uniform" in quals:
            for dc in d["declarators"]:
                self.uniforms.append({"name": dc["name"], "type": self.type_of_name(base_t)})
        else:
            for dc in d["declarators"]:
                self.globals.append(
                    {
                        "name": dc["name"],
                        "type": self.type_of_name(base_t, dc.get("array")),
                        "init": dc.get("init"),
                        "array": dc.get("array"),
                    }
                )

    # ---- emit ----
    def emit(self):
        self.collect()
        for u in self.uniforms:
            self.root.define(u["name"], u["type"], f"_u_{py_ident(u['name'])}")
        for g in self.globals:
            py = "ctx.uv" if g["name"] in self.varyings else f"g.{py_ident(g['name'])}"
            self.root.define(g["name"], g["type"], py)

        L = [
            "def run_pixel(ctx, out):",
            "    rt = ctx.rt",
            "    U = ctx.uniforms",
            "    T = ctx.textures",
            "    class _G:",
            "        pass",
            "    g = _G()",
        ]
        for u in self.uniforms:
            if base_of(u["type"]) == "sampler":
                L.append(f"    _u_{py_ident(u['name'])} = T[{q(u['name'])}]")
            else:
                # WebGL zero-initializes unbound uniforms; a vestigial uniform not
                # in the effect's params is simply absent from U. Default it rather
                # than KeyError-ing (samplers fall back via _DefaultTex.__missing__).
                L.append(f"    _u_{py_ident(u['name'])} = U.get({q(u['name'])}, {self._default(u['type'])})")
        for g in self.globals:
            if g["name"] in self.varyings:
                continue
            # Uninitialized globals still need their attribute created on `g`
            # (e.g. `float emboss[9];` filled later inside a helper). Mirror the
            # local-decl defaulting: array -> new_array, else type default.
            if g["init"] is not None:
                code, _ = self.expr(g["init"], self.root)
            elif g.get("array") is not None:
                n_code = self.expr(g["array"], self.root)[0] if g["array"] not in (None, True) else "0"
                code = f"rt.new_array({n_code}, {g['type']['width']})"
            else:
                code = self._default(g["type"])
            L.append(f"    g.{py_ident(g['name'])} = {code}")

        main = None
        for fn in self.funcs:
            if fn["node"]["name"] == "main":
                main = fn
                continue
            self._emit_func(L, fn)
        if main is None:
            raise SyntaxError("shader has no main()")
        self._emit_func(L, main)
        L.append(f"    {main['mangled']}()")
        out_name = "ctx.uv" if self.outputs[0] in self.varyings else f"g.{py_ident(self.outputs[0])}"
        L.append(f"    _c = {out_name}")
        L.append("    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])")
        if self.uses_deriv:
            L.append("run_pixel.uses_derivatives = True")
        return "\n".join(L) + "\n"

    def _emit_func(self, L, fn, indent=1):
        pad = "    " * indent
        scope = self.root.child()
        pynames = []
        for p, t in zip(fn["node"]["params"], fn["ptypes"], strict=True):
            if p[1] is None:
                pynames.append("_unused")
                continue
            pynames.append(scope.define(p[1], t)["py"])
        L.append(f"{pad}def {fn['mangled']}({', '.join(pynames)}):")
        for p, t in zip(fn["node"]["params"], fn["ptypes"], strict=True):
            if p[1] and width_of(t) > 1:
                L.append(f"{pad}    {py_ident(p[1])} = rt.copy({py_ident(p[1])}, {q(base_of(t))})")
        out_pynames = [pynames[i] for i in fn.get("out_idxs", [])]
        prev = self.cur_out
        self.cur_out = out_pynames
        body = self.block(fn["node"]["body"], scope, indent + 1)
        if out_pynames:  # out/inout params: every exit returns (retval, *outs)
            body.append(f"{'    ' * (indent + 1)}return (None, {', '.join(out_pynames)})")
        self.cur_out = prev
        if not body:
            body = [f"{'    ' * (indent + 1)}pass"]
        L.extend(body)

    def block(self, stmts, scope, indent):
        out = []
        for s in stmts:
            self.stmt(s, scope, indent, out)
        return out

    def stmt(self, s, scope, indent, out):
        pad = "    " * indent
        k = s["k"]
        if k == "block":
            out.extend(self.block(s["body"], scope.child(), indent) or [f"{pad}pass"])
        elif k == "decl":
            for dc in s["declarators"]:
                t = self.type_of_name(s["type"], dc.get("array"))
                # Resolve the initializer in the ENCLOSING scope, before the new
                # name is defined (GLSL `float time = time;` reads the outer time).
                init_code = self.expr(dc["init"], scope)[0] if dc.get("init") is not None else None
                e = scope.define(dc["name"], t)
                if init_code is not None:
                    out.append(f"{pad}{e['py']} = {init_code}")
                elif dc.get("array") is not None:
                    n_code = self.expr(dc["array"], scope)[0] if dc["array"] not in (None, True) else "0"
                    out.append(f"{pad}{e['py']} = rt.new_array({n_code}, {t['width']})")
                else:
                    out.append(f"{pad}{e['py']} = {self._default(t)}")
        elif k == "expr":
            code, _ = self.expr(s["expr"], scope)
            out.append(f"{pad}{code}")
        elif k == "if":
            code, _ = self.expr(s["cond"], scope)
            # A runtime #if lowered to a real if/else keeps GLSL block scope, but
            # a preprocessor #if leaves its declarations at the ENCLOSING scope —
            # they may be read after #endif or in a sibling lowered-#if block.
            # Real GLSL never declares in a branch and reads it after (won't
            # compile), so hoisting every branch decl to the enclosing scope
            # (with a default init, since a single-arm #if may not run) is safe
            # and only affects lowered #if.
            hoist = dict(self._branch_decls(s["then"]))
            if s.get("els") is not None:
                hoist.update(self._branch_decls(s["els"]))
            for name, typ in hoist.items():
                if scope.resolve(name) is None:
                    e = scope.define(name, typ)
                    out.append(f"{pad}{e['py']} = {self._default(typ)}")
            out.append(f"{pad}if {code}:")
            out.extend(self._branch(s["then"], scope, indent + 1))
            if s.get("els") is not None:
                out.append(f"{pad}else:")
                out.extend(self._branch(s["els"], scope, indent + 1))
        elif k == "for":
            self._for(s, scope, indent, out)
        elif k in ("while", "dowhile"):
            lid = self.loop_id
            self.loop_id += 1
            out.append(f"{pad}for _wh{lid} in range(1048576):")
            code, _ = self.expr(s["cond"], scope)
            out.append(f"{pad}    if not ({code}):")
            out.append(f"{pad}        break")
            out.extend(self._branch(s["body"], scope.child(), indent + 1))
        elif k == "return":
            val_node = s.get("value")
            # GLSL permits `return x = expr;` / `return x *= expr;` — assignment
            # is an expression yielding the assigned value. Python assignment is a
            # statement, so hoist it: emit the assignment, then return the target.
            if val_node is not None and val_node.get("k") == "assign":
                stmt_code, _ = self._e_assign(val_node, scope)
                out.append(f"{pad}{stmt_code}")
                val_node = val_node["target"]
            if self.cur_out:
                val = self.expr(val_node, scope)[0] if val_node is not None else "None"
                out.append(f"{pad}return ({val}, {', '.join(self.cur_out)})")
            elif val_node is None:
                out.append(f"{pad}return")
            else:
                code, _ = self.expr(val_node, scope)
                out.append(f"{pad}return {code}")
        elif k == "break":
            out.append(f"{pad}break")
        elif k == "continue":
            out.append(f"{pad}continue")
        elif k == "discard":
            out.append(f"{pad}return")
        else:
            raise SyntaxError(f"codegen: unhandled statement {k}")

    def _branch(self, s, scope, indent):
        out = []
        if s["k"] == "block":
            out.extend(self.block(s["body"], scope.child(), indent))
        else:
            self.stmt(s, scope.child(), indent, out)
        return out or [f"{'    ' * indent}pass"]

    def _branch_decls(self, s):
        """Names (mapped to type) a branch may declare at its top level — the
        UNION over if/elif/else arms. Used to hoist lowered-#if declarations to
        the enclosing scope (each hoisted name gets a default init at the hoist
        site, so an arm that doesn't run still leaves the name bound)."""
        if s is None:
            return {}
        k = s.get("k")
        if k == "block":
            decls = {}
            for st in s["body"]:
                if st.get("k") == "decl":
                    for dc in st["declarators"]:
                        decls[dc["name"]] = self.type_of_name(st["type"], dc.get("array"))
            return decls
        if k == "decl":
            return {dc["name"]: self.type_of_name(s["type"], dc.get("array")) for dc in s["declarators"]}
        if k == "if":
            d = dict(self._branch_decls(s["then"]))
            d.update(self._branch_decls(s.get("els")))
            return d
        return {}

    def _for(self, s, scope, indent, out):
        pad = "    " * indent
        lid = self.loop_id
        self.loop_id += 1
        ls = scope.child()
        if s.get("init"):
            self.stmt(s["init"], ls, indent, out)
        out.append(f"{pad}_for{lid}_first = True")
        out.append(f"{pad}for _for{lid} in range(1048576):")
        upd = []
        if s.get("update"):
            code, _ = self.expr(s["update"], ls)
            upd.append(f"{pad}        {code}")
        out.append(f"{pad}    if not _for{lid}_first:")
        out.extend(upd or [f"{pad}        pass"])
        out.append(f"{pad}    _for{lid}_first = False")
        if s.get("cond"):
            code, _ = self.expr(s["cond"], ls)
            out.append(f"{pad}    if not ({code}):")
            out.append(f"{pad}        break")
        out.extend(self._branch(s["body"], ls, indent + 1))

    def _default(self, t):
        if base_of(t) == "struct":
            fields = self.structs.get(t.get("struct"), [])
            return "[" + ", ".join(self._default(self.type_of_name(f[0])) for f in fields) + "]"
        if width_of(t) == 1:
            return "False" if base_of(t) == "bool" else ("0" if base_of(t) in ("int", "uint") else "rt.f(0.0)")
        return f"rt.construct({t['width']}, 0.0{_construct_base(t)})"

    # ---- expressions -> (code, type) ----
    def expr(self, node, scope):
        k = node["k"]
        return getattr(self, f"_e_{k}")(node, scope)

    def _e_num(self, node, scope):
        raw = node["value"]
        low = raw.lower()
        if low.endswith("u"):
            return (f"rt.i({int(raw[:-1], 0)})", TYPE["uint"])
        if raw.lower().startswith("0x"):
            return (f"rt.i({int(raw, 16)})", TYPE["int"])
        if "." in raw or "e" in low or low.endswith("f"):
            return (f"rt.f({float(raw.rstrip('fF'))})", FLOAT)
        return (f"rt.i({int(raw)})", TYPE["int"])

    def _e_bool(self, node, scope):
        return ("True" if node["value"] else "False", BOOL)

    def _e_id(self, node, scope):
        name = node["name"]
        if name == "gl_FragCoord":
            return ("ctx.frag_coord", VEC4)
        e = scope.resolve(name)
        if not e:
            if name in ("v_texCoord", "vTexCoord", "texCoord"):  # undeclared fragment varying
                return ("ctx.uv", TYPE["vec2"])
            raise SyntaxError(f"codegen: unresolved identifier {name!r}")
        return (e["py"], e["type"])

    def _e_member(self, node, scope):
        obj_code, obj_t = self.expr(node["obj"], scope)
        field = node["field"]
        if base_of(obj_t) == "struct":
            fields = self.structs.get(obj_t.get("struct"), [])
            idx = next((i for i, f in enumerate(fields) if f[1] == field), 0)
            ftype = self.type_of_name(fields[idx][0]) if fields else FLOAT
            return (f"{obj_code}[{idx}]", ftype)
        w = len(field)
        t = {"base": base_of(obj_t), "width": w}
        return (f"rt.swizzle({obj_code}, {q(field)})", t)

    def _e_index(self, node, scope):
        obj_code, obj_t = self.expr(node["obj"], scope)
        idx_code, _ = self.expr(node["idx"], scope)
        if obj_t.get("mat"):
            n = obj_t["mat"]
            return (f"rt.mat_col({obj_code}, {idx_code}, {n})", {"base": "float", "width": n})
        if obj_t.get("array"):
            return (f"{obj_code}[int({idx_code})]", {"base": base_of(obj_t), "width": obj_t["width"]})
        return (f"{obj_code}[int({idx_code})]", {"base": base_of(obj_t), "width": 1})

    def _e_unary(self, node, scope):
        if node["op"] in ("++", "--"):  # prefix
            return self._incdec(node["x"], node["op"], scope)
        code, t = self.expr(node["x"], scope)
        if node["op"] == "!":
            return (f"(not ({code}))", BOOL)
        if node["op"] == "~":
            return (f"rt.bit_not({code})", t)
        return (f"rt.unary({q(node['op'])}, {code})", t)

    def _e_post(self, node, scope):
        return self._incdec(node["x"], node["op"], scope)

    def _incdec(self, target, op, scope):
        code, t = self.expr(target, scope)
        base = "+" if op == "++" else "-"
        b = "uint" if base_of(t) == "uint" else ("int" if base_of(t) == "int" else "float")
        return (f"{code} = rt.binary({q(base)}, {code}, rt.i(1), {width_of(t)}, {q(b)})", t)

    def _e_cond(self, node, scope):
        c_code, _ = self.expr(node["c"], scope)
        a_code, a_t = self.expr(node["a"], scope)
        b_code, b_t = self.expr(node["b"], scope)
        w = max(width_of(a_t), width_of(b_t))
        return (f"({a_code} if {c_code} else {b_code})", {"base": base_of(a_t), "width": w})

    def _e_binary(self, node, scope):
        op = node["op"]
        l_code, l_t = self.expr(node["l"], scope)
        r_code, r_t = self.expr(node["r"], scope)
        if op in ("==", "!=", "<", ">", "<=", ">=", "&&", "||"):
            pyop = {"&&": "and", "||": "or"}.get(op)
            if pyop:
                return (f"(bool({l_code}) {pyop} bool({r_code}))", BOOL)
            return (f"rt.binary({q(op)}, {l_code}, {r_code})", BOOL)
        if op == "*" and (l_t.get("mat") or r_t.get("mat")) and width_of(l_t) > 1 and width_of(r_t) > 1:
            dim = l_t.get("mat") or r_t.get("mat")
            both = l_t.get("mat") and r_t.get("mat")
            t = {"base": "float", "width": dim * dim, "mat": dim} if both else {"base": "float", "width": dim}
            return (f"rt.matrix_mult({l_code}, {r_code}, {dim})", t)
        width = max(width_of(l_t), width_of(r_t))
        lb, rb = base_of(l_t), base_of(r_t)
        if lb == "uint" or rb == "uint":
            base = "uint"
        elif (lb == "int" and rb == "int") or op in ("&", "|", "^", "<<", ">>", "%"):
            base = "int"
        else:
            base = "float"
        return (f"rt.binary({q(op)}, {l_code}, {r_code}, {width}, {q(base)})", {"base": base, "width": width})

    def _e_assign(self, node, scope):
        op = node["op"]
        target = node["target"]
        v_code, _v_t = self.expr(node["value"], scope)
        base_op = None if op == "=" else op[:-1]
        tcode, tt = self.expr(target, scope)
        if target["k"] == "id" or target["k"] == "index":
            if base_op:
                b = "uint" if base_of(tt) == "uint" else ("int" if base_of(tt) == "int" else "float")
                rhs = f"rt.binary({q(base_op)}, {tcode}, {v_code}, {width_of(tt)}, {q(b)})"
            else:
                rhs = v_code
            # JS's glsl-transpiler reuses a pooled Float32Array for a vector variable:
            # reassignment mutates it in place, so a prior alias (`vec2 prev = cur;`,
            # which both engines emit as a reference, not a copy) tracks the update.
            # Rebinding to a fresh array instead breaks that alias and diverges from
            # the oracle — e.g. parallax's ray-march refinement, where prevUV aliases
            # rayUV and `mix(rayUV, prevUV, w)` collapses to a no-op. Mutate vectors in
            # place to match; scalars are immutable and index targets already do.
            if target["k"] == "id" and width_of(tt) > 1:
                return (f"{tcode}[:] = {rhs}", tt)
            return (f"{tcode} = {rhs}", tt)
        if target["k"] == "member":
            obj_code, obj_t = self.expr(target["obj"], scope)
            if base_of(obj_t) == "struct":
                fields = self.structs.get(obj_t.get("struct"), [])
                idx = next((i for i, f in enumerate(fields) if f[1] == target["field"]), 0)
                return (f"{obj_code}[{idx}] = {v_code}", tt)
            sw = target["field"]
            if base_op:
                cur = f"rt.swizzle({obj_code}, {q(sw)})"
                ob = base_of(obj_t)
                b = "uint" if ob == "uint" else ("int" if ob == "int" else "float")
                rhs = f"rt.binary({q(base_op)}, {cur}, {v_code}, {len(sw)}, {q(b)})"
            else:
                rhs = v_code
            return (
                f"{obj_code} = rt.assign_swizzle({obj_code}, {q(sw)}, {rhs})",
                {"base": base_of(obj_t), "width": len(sw)},
            )
        raise SyntaxError(f"codegen: bad assignment target {target['k']}")

    def _e_construct(self, node, scope):
        tname = node["type"]
        args = [self.expr(a, scope) for a in node["args"]]
        elems = ", ".join(a[0] for a in args)
        if node.get("array") is not None:  # array constructor TYPE[N](...)
            elt = TYPE.get(tname, FLOAT)
            return (f"rt.array([{elems}])", {"base": elt["base"], "width": elt["width"], "array": True})
        if tname in self.structs:
            return (f"[{elems}]", {"base": "struct", "width": 0, "struct": tname})
        t = TYPE.get(tname, {"base": "float", "width": max((width_of(a[1]) for a in args), default=1)})
        return (f"rt.construct({t['width']}, {elems}{_construct_base(t)})", t)

    def _e_call(self, node, scope):
        name = node["name"]
        args = [self.expr(a, scope) for a in node["args"]]
        codes = [a[0] for a in args]
        if name in ("dFdx", "dFdy", "fwidth"):
            self.uses_deriv = True
            return (f"rt.{name}({codes[0]})", args[0][1])
        r = _ROUTED.get(name)
        if r:
            return r(self, codes, args)
        if name in self.overloads:
            fn = self._resolve_overload(name, [a[1] for a in args])
            if fn.get("out_idxs"):  # out/inout: unpack outputs back to caller lvalues
                targets = [self.expr(node["args"][i], scope)[0] for i in fn["out_idxs"]]
                return (f"_retc, {', '.join(targets)} = {fn['mangled']}({', '.join(codes)})", fn["ret"])
            return (f"{fn['mangled']}({', '.join(codes)})", fn["ret"])
        if name in TYPE:  # scalar cast: int(x), float(x), uint(x)
            t = TYPE[name]
            return (f"rt.construct({t['width']}, {', '.join(codes)}{_construct_base(t)})", t)
        # component-wise builtin
        width = max((width_of(a[1]) for a in args), default=1)
        base = "int" if all(base_of(a[1]) in ("int", "uint") for a in args) and args else "float"
        return (f"rt.component_wise({q(name)}, {', '.join(codes)}, width={width})", {"base": base, "width": width})

    def _resolve_overload(self, name, argtypes):
        cands = self.overloads[name]
        if len(cands) == 1:
            return cands[0]
        same = [c for c in cands if len(c["ptypes"]) == len(argtypes)]
        exact = next(
            (
                c
                for c in same
                if all(
                    base_of(p) == base_of(a) and width_of(p) == width_of(a)
                    for p, a in zip(c["ptypes"], argtypes, strict=True)
                )
            ),
            None,
        )
        return exact or (same[0] if same else cands[0])


def _type_name(t):
    for k, v in TYPE.items():
        if v.get("base") == t.get("base") and v.get("width") == t.get("width") and v.get("mat") == t.get("mat"):
            return k
    return f"{base_of(t)}{width_of(t)}"


# name -> (codegen, arg_codes, args) -> (code, type)
_ROUTED = {
    "texture": lambda g, c, a: (f"rt.texture({c[0]}, {c[1]})", VEC4),
    "textureLod": lambda g, c, a: (f"rt.texture({c[0]}, {c[1]})", VEC4),
    "texelFetch": lambda g, c, a: (f"rt.texel_fetch({c[0]}, {c[1]}, {c[2] if len(c) > 2 else '0'})", VEC4),
    "textureSize": lambda g, c, a: (f"rt.texture_size({c[0]})", TYPE["ivec2"]),
    "length": lambda g, c, a: (f"rt.length({c[0]})", FLOAT),
    "__array_length": lambda g, c, a: (f"len({c[0]})", TYPE["int"]),
    "distance": lambda g, c, a: (f"rt.distance({c[0]}, {c[1]})", FLOAT),
    "dot": lambda g, c, a: (f"rt.dot({c[0]}, {c[1]})", FLOAT),
    "normalize": lambda g, c, a: (f"rt.normalize({c[0]})", a[0][1]),
    "cross": lambda g, c, a: (f"rt.cross({c[0]}, {c[1]})", a[0][1]),
    "reflect": lambda g, c, a: (f"rt.reflect({c[0]}, {c[1]})", a[0][1]),
    "refract": lambda g, c, a: (f"rt.refract({c[0]}, {c[1]}, {c[2]})", a[0][1]),
    "pcg3d": lambda g, c, a: (f"rt.pcg3d({c[0]})", TYPE["uvec3"]),
    "cpu_umul": lambda g, c, a: (f"rt.binary('*', {c[0]}, {c[1]}, 1, 'uint')", TYPE["uint"]),
    "hashUint": lambda g, c, a: (f"rt.hash_uint({c[0]})", TYPE["uint"]),
    "hash_uint": lambda g, c, a: (f"rt.hash_uint({c[0]})", TYPE["uint"]),
    "floatBitsToUint": lambda g, c, a: (f"rt.float_bits_to_uint({c[0]})", TYPE["uint"]),
    "uintBitsToFloat": lambda g, c, a: (f"rt.uint_bits_to_float({c[0]})", FLOAT),
    "packHalf2x16": lambda g, c, a: (f"rt.pack_half_2x16({c[0]})", TYPE["uint"]),
    "unpackHalf2x16": lambda g, c, a: (f"rt.unpack_half_2x16({c[0]})", TYPE["vec2"]),
    "cpu_float": lambda g, c, a: (f"rt.construct(1, {c[0]})", FLOAT),
    "cpu_ivec2": lambda g, c, a: (f"rt.construct(2, {', '.join(c)}, base='int')", TYPE["ivec2"]),
    "cpu_ivec3": lambda g, c, a: (f"rt.construct(3, {', '.join(c)}, base='int')", TYPE["ivec3"]),
    "cpu_uvec2": lambda g, c, a: (f"rt.construct(2, {', '.join(c)}, base='uint')", TYPE["uvec2"]),
    "cpu_uvec3": lambda g, c, a: (f"rt.construct(3, {', '.join(c)}, base='uint')", TYPE["uvec3"]),
}

# functions whose GLSL definitions (emitted by normalize) are overridden by the
# runtime routing above, so we must NOT emit them as user functions.
_SKIP_FUNCS = {"cpu_umul", "cpu_ivec2", "cpu_ivec3", "cpu_ivec4", "cpu_uvec2", "cpu_uvec3", "cpu_uvec4", "cpu_float"}


def emit_python(program, outputs=None, varyings=None):
    gen = CodeGen(program, outputs, varyings)
    gen.funcs_filter = _SKIP_FUNCS
    # drop overridden helper functions before emit
    program["decls"] = [d for d in program["decls"] if not (d.get("k") == "func" and d.get("name") in _SKIP_FUNCS)]
    return gen.emit()
