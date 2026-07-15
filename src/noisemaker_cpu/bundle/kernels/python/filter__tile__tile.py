def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_symmetry = U["symmetry"]
    _u_scale = U["scale"]
    _u_offsetX = U["offsetX"]
    _u_offsetY = U["offsetY"]
    _u_angle = U["angle"]
    _u_repeat = U["repeat"]
    _u_aspectLens = U["aspectLens"]
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    def rot__vec2_float(p, a):
        p = rt.copy(p)
        c = rt.component_wise("cos", a, width=1)
        s = rt.component_wise("sin", a, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1), rt.binary("*", rt.swizzle(p, "y"), s, 1), 1), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1), rt.binary("*", rt.swizzle(p, "y"), c, 1), 1))
    def mirrorFold__float(t):
        return rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), rt.component_wise("fract", rt.binary("*", t, rt.f(0.5), 1), width=1), 1), rt.f(1.0), 1), width=1), 1)
    def hexCoord__vec2(uv):
        uv = rt.copy(uv)
        s = rt.construct(2, rt.f(1.0), rt.f(1.7320508))
        h = rt.binary("*", s, rt.f(0.5), 2)
        a = rt.binary("-", rt.component_wise("mod", uv, s, width=2), h, 2)
        b = rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, h, 2), s, width=2), h, 2)
        return (a if rt.binary("<", rt.dot(a, a), rt.dot(b, b)) else b)
    def rotationalFold__vec2_int(uv, n):
        uv = rt.copy(uv)
        fn = n
        sectorAngle = rt.binary("/", g.TAU, fn, 1)
        p = rt.binary("-", uv, rt.f(0.5), 2)
        a = rt.component_wise("atan", rt.swizzle(p, "y"), rt.swizzle(p, "x"), width=1)
        r = rt.length(p)
        a = rt.component_wise("mod", rt.component_wise("mod", rt.binary("+", a, g.TAU, 1), g.TAU, width=1), sectorAngle, width=1)
        if rt.binary(">", a, rt.binary("*", sectorAngle, rt.f(0.5), 1)):
            a = rt.binary("-", sectorAngle, a, 1)
        return rt.binary("+", rt.construct(2, rt.binary("*", r, rt.component_wise("cos", a, width=1), 1), rt.binary("*", r, rt.component_wise("sin", a, width=1), 1)), rt.f(0.5), 2)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2)
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        st = rt.binary("-", globalUV, rt.f(0.5), 2)
        if _u_aspectLens:
            st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), aspect, 1))
        st = rot__vec2_float(st, rt.binary("/", rt.binary("*", _u_angle, g.PI, 1), rt.f(180.0), 1))
        if _u_aspectLens:
            st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), aspect, 1))
        st = rt.binary("+", st, rt.f(0.5), 2)
        rep = (rt.construct(2, rt.binary("*", _u_repeat, aspect, 1), _u_repeat) if _u_aspectLens else rt.construct(2, _u_repeat))
        if rt.binary("==", _u_symmetry, rt.i(3)):
            local = hexCoord__vec2(rt.binary("*", rt.binary("+", st, rt.construct(2, _u_offsetX, _u_offsetY), 2), rep, 2))
            local = rt.binary("/", local, _u_scale, 2)
            st = rotationalFold__vec2_int(rt.binary("+", local, rt.f(0.5), 2), rt.i(6))
        else:
            st = rt.binary("*", st, rep, 2)
            st = rt.component_wise("fract", st, width=2)
            effectiveScale = (rt.binary("*", _u_scale, rt.f(0.5), 1) if rt.binary("==", _u_symmetry, rt.i(0)) else _u_scale)
            st = rt.binary("/", rt.binary("-", st, rt.f(0.5), 2), effectiveScale, 2)
            st = rt.binary("+", st, rt.binary("+", rt.f(0.5), rt.construct(2, _u_offsetX, _u_offsetY), 2), 2)
            if rt.binary("==", _u_symmetry, rt.i(0)):
                st = rt.assign_swizzle(st, "x", mirrorFold__float(rt.swizzle(st, "x")))
                st = rt.assign_swizzle(st, "y", mirrorFold__float(rt.swizzle(st, "y")))
            else:
                if rt.binary("==", _u_symmetry, rt.i(1)):
                    st = rotationalFold__vec2_int(rt.component_wise("fract", st, width=2), rt.i(2))
                else:
                    st = rotationalFold__vec2_int(rt.component_wise("fract", st, width=2), rt.i(4))
        localUV = rt.component_wise("fract", st, width=2)
        g.fragColor = rt.construct(4, rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
