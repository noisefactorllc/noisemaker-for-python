def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_size = U.get("size", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        icenter = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        dims = rt.texture_size(_u_inputTex)
        radius = rt.f(0.0)
        if rt.binary("==", _u_MODE, rt.i(0)):
            radius = rt.component_wise("min", _u_size, rt.f(3.0), width=1)
        else:
            radius = _u_size
        fr = rt.component_wise("clamp", radius, rt.f(1.0), rt.f(12.0), width=1)
        frSq = rt.binary("*", fr, fr, 1, "float")
        sampleLimit = rt.construct(1, rt.component_wise("ceil", fr, width=1), base="int")
        m0 = rt.construct(3, rt.f(0.0))
        m1 = rt.construct(3, rt.f(0.0))
        m2 = rt.construct(3, rt.f(0.0))
        m3 = rt.construct(3, rt.f(0.0))
        m4 = rt.construct(3, rt.f(0.0))
        m5 = rt.construct(3, rt.f(0.0))
        m6 = rt.construct(3, rt.f(0.0))
        m7 = rt.construct(3, rt.f(0.0))
        q0 = rt.construct(3, rt.f(0.0))
        q1 = rt.construct(3, rt.f(0.0))
        q2 = rt.construct(3, rt.f(0.0))
        q3 = rt.construct(3, rt.f(0.0))
        q4 = rt.construct(3, rt.f(0.0))
        q5 = rt.construct(3, rt.f(0.0))
        q6 = rt.construct(3, rt.f(0.0))
        q7 = rt.construct(3, rt.f(0.0))
        n0 = rt.f(0.0)
        n1 = rt.f(0.0)
        n2 = rt.f(0.0)
        n3 = rt.f(0.0)
        n4 = rt.f(0.0)
        n5 = rt.f(0.0)
        n6 = rt.f(0.0)
        n7 = rt.f(0.0)
        y = rt.unary("-", sampleLimit)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, sampleLimit)):
                break
            x = rt.unary("-", sampleLimit)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, sampleLimit)):
                    break
                d = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                if (bool((bool(rt.binary(">", rt.component_wise("abs", rt.swizzle(d, "x"), width=1), fr)) or bool(rt.binary(">", rt.component_wise("abs", rt.swizzle(d, "y"), width=1), fr)))) or bool(rt.binary(">", rt.dot(d, d), frSq))):
                    continue
                if (bool((bool(rt.binary(">", fr, rt.f(8.0))) and bool(rt.binary(">", rt.dot(d, d), rt.f(64.0))))) and bool(rt.binary("!=", rt.binary("%", rt.binary("+", rt.component_wise("abs", x, width=1), rt.component_wise("abs", y, width=1), 1, "int"), rt.i(2), 1, "int"), rt.i(0)))):
                    continue
                sc = rt.component_wise("clamp", rt.binary("+", icenter, rt.construct(2, x, y, base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", dims, rt.construct(2, rt.i(1), base="int"), 2, "int"), width=2)
                c = rt.swizzle(rt.texel_fetch(_u_inputTex, sc, rt.i(0)), "rgb")
                cc = rt.binary("*", c, c, 3, "float")
                if (bool(rt.binary("==", x, rt.i(0))) and bool(rt.binary("==", y, rt.i(0)))):
                    m4[:] = rt.binary("+", m4, c, 3, "float")
                    q4[:] = rt.binary("+", q4, cc, 3, "float")
                    n4 = rt.binary("+", n4, rt.f(1.0), 1, "float")
                else:
                    if (bool(rt.binary(">", rt.swizzle(d, "x"), rt.f(0.0))) and bool(rt.binary(">=", rt.swizzle(d, "y"), rt.f(0.0)))):
                        if rt.binary("<=", rt.component_wise("abs", rt.swizzle(d, "x"), width=1), rt.component_wise("abs", rt.swizzle(d, "y"), width=1)):
                            m5[:] = rt.binary("+", m5, c, 3, "float")
                            q5[:] = rt.binary("+", q5, cc, 3, "float")
                            n5 = rt.binary("+", n5, rt.f(1.0), 1, "float")
                        else:
                            m4[:] = rt.binary("+", m4, c, 3, "float")
                            q4[:] = rt.binary("+", q4, cc, 3, "float")
                            n4 = rt.binary("+", n4, rt.f(1.0), 1, "float")
                    else:
                        if (bool(rt.binary("<=", rt.swizzle(d, "x"), rt.f(0.0))) and bool(rt.binary(">", rt.swizzle(d, "y"), rt.f(0.0)))):
                            if rt.binary("<", rt.component_wise("abs", rt.swizzle(d, "x"), width=1), rt.component_wise("abs", rt.swizzle(d, "y"), width=1)):
                                m6[:] = rt.binary("+", m6, c, 3, "float")
                                q6[:] = rt.binary("+", q6, cc, 3, "float")
                                n6 = rt.binary("+", n6, rt.f(1.0), 1, "float")
                            else:
                                m7[:] = rt.binary("+", m7, c, 3, "float")
                                q7[:] = rt.binary("+", q7, cc, 3, "float")
                                n7 = rt.binary("+", n7, rt.f(1.0), 1, "float")
                        else:
                            if (bool(rt.binary("<", rt.swizzle(d, "x"), rt.f(0.0))) and bool(rt.binary("<=", rt.swizzle(d, "y"), rt.f(0.0)))):
                                if rt.binary("<=", rt.component_wise("abs", rt.swizzle(d, "x"), width=1), rt.component_wise("abs", rt.swizzle(d, "y"), width=1)):
                                    m1[:] = rt.binary("+", m1, c, 3, "float")
                                    q1[:] = rt.binary("+", q1, cc, 3, "float")
                                    n1 = rt.binary("+", n1, rt.f(1.0), 1, "float")
                                else:
                                    m0[:] = rt.binary("+", m0, c, 3, "float")
                                    q0[:] = rt.binary("+", q0, cc, 3, "float")
                                    n0 = rt.binary("+", n0, rt.f(1.0), 1, "float")
                            else:
                                if rt.binary("<", rt.component_wise("abs", rt.swizzle(d, "x"), width=1), rt.component_wise("abs", rt.swizzle(d, "y"), width=1)):
                                    m2[:] = rt.binary("+", m2, c, 3, "float")
                                    q2[:] = rt.binary("+", q2, cc, 3, "float")
                                    n2 = rt.binary("+", n2, rt.f(1.0), 1, "float")
                                else:
                                    m3[:] = rt.binary("+", m3, c, 3, "float")
                                    q3[:] = rt.binary("+", q3, cc, 3, "float")
                                    n3 = rt.binary("+", n3, rt.f(1.0), 1, "float")
        bestC = rt.construct(3, rt.f(0.0))
        bestV = rt.f(1000000000.0)
        m = rt.construct(3, 0.0)
        v = rt.construct(3, 0.0)
        tv = rt.f(0.0)
        if rt.binary(">=", n0, rt.f(1.0)):
            m = rt.binary("/", m0, n0, 3, "float")
            v = rt.binary("-", rt.binary("/", q0, n0, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n1, rt.f(1.0)):
            m = rt.binary("/", m1, n1, 3, "float")
            v = rt.binary("-", rt.binary("/", q1, n1, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n2, rt.f(1.0)):
            m = rt.binary("/", m2, n2, 3, "float")
            v = rt.binary("-", rt.binary("/", q2, n2, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n3, rt.f(1.0)):
            m = rt.binary("/", m3, n3, 3, "float")
            v = rt.binary("-", rt.binary("/", q3, n3, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n4, rt.f(1.0)):
            m = rt.binary("/", m4, n4, 3, "float")
            v = rt.binary("-", rt.binary("/", q4, n4, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n5, rt.f(1.0)):
            m = rt.binary("/", m5, n5, 3, "float")
            v = rt.binary("-", rt.binary("/", q5, n5, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n6, rt.f(1.0)):
            m = rt.binary("/", m6, n6, 3, "float")
            v = rt.binary("-", rt.binary("/", q6, n6, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        if rt.binary(">=", n7, rt.f(1.0)):
            m = rt.binary("/", m7, n7, 3, "float")
            v = rt.binary("-", rt.binary("/", q7, n7, 3, "float"), rt.binary("*", m, m, 3, "float"), 3, "float")
            tv = rt.binary("+", rt.binary("+", rt.swizzle(v, "r"), rt.swizzle(v, "g"), 1, "float"), rt.swizzle(v, "b"), 1, "float")
            if rt.binary("<", tv, bestV):
                bestV = tv
                bestC[:] = m
        g.fragColor[:] = rt.construct(4, bestC, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
