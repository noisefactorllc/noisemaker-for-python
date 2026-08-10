def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_angle = U.get("angle", rt.f(0.0))
    _u_blurDistance = U.get("blurDistance", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.N = rt.i(32)
    def hash12__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def main__void():
        dir = rt.construct(2, rt.component_wise("cos", rt.component_wise("radians", _u_angle, width=1), width=1), rt.component_wise("sin", rt.component_wise("radians", _u_angle, width=1), width=1))
        tapStep = rt.binary("/", _u_blurDistance, rt.construct(1, rt.binary("-", g.N, rt.i(1), 1, "int")), 1, "float")
        jitter = rt.binary("*", rt.binary("-", hash12__vec2(rt.swizzle(ctx.frag_coord, "xy")), rt.f(0.5), 1, "float"), tapStep, 1, "float")
        sum = rt.construct(4, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, g.N)):
                break
            t = rt.binary("+", rt.binary("*", rt.binary("-", rt.binary("/", rt.construct(1, i), rt.construct(1, rt.binary("-", g.N, rt.i(1), 1, "int")), 1, "float"), rt.f(0.5), 1, "float"), _u_blurDistance, 1, "float"), jitter, 1, "float")
            offset = rt.binary("*", dir, t, 2, "float")
            sum[:] = rt.binary("+", sum, rt.texture(_u_inputTex, rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), offset, 2, "float"), _u_resolution, 2, "float")), 4, "float")
        g.fragColor[:] = rt.binary("/", sum, rt.construct(1, g.N), 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
