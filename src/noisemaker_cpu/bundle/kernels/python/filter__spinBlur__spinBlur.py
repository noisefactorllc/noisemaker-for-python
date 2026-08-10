def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_amount = U.get("amount", rt.f(0.0))
    _u_centerX = U.get("centerX", rt.f(0.0))
    _u_centerY = U.get("centerY", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.N = rt.i(32)
    def hash12__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def rotateAround__vec2_vec2_float_float(uv, center, angle, aspectRatio):
        uv = rt.copy(uv, "float")
        center = rt.copy(center, "float")
        p = uv
        p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), aspectRatio, 1, "float"))
        c = center
        c = rt.assign_swizzle(c, "x", rt.binary("*", rt.swizzle(c, "x"), aspectRatio, 1, "float"))
        p[:] = rt.binary("-", p, c, 2, "float")
        s = rt.component_wise("sin", angle, width=1)
        co = rt.component_wise("cos", angle, width=1)
        p[:] = rt.matrix_mult(rt.construct(4, co, rt.unary("-", s), s, co), p, 2)
        p[:] = rt.binary("+", p, c, 2, "float")
        p = rt.assign_swizzle(p, "x", rt.binary("/", rt.swizzle(p, "x"), aspectRatio, 1, "float"))
        return p
    def main__void():
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        center = rt.construct(2, _u_centerX, _u_centerY)
        arc = rt.component_wise("radians", _u_amount, width=1)
        angularStep = rt.binary("/", arc, rt.construct(1, rt.binary("-", g.N, rt.i(1), 1, "int")), 1, "float")
        jitterCoord = rt.construct(2, rt.swizzle(globalCoord, "x"), rt.component_wise("abs", rt.binary("-", rt.swizzle(globalCoord, "y"), rt.binary("*", rt.swizzle(_u_fullResolution, "y"), rt.f(0.5), 1, "float"), 1, "float"), width=1))
        jitter = rt.binary("*", rt.binary("-", hash12__vec2(jitterCoord), rt.f(0.5), 1, "float"), angularStep, 1, "float")
        sum = rt.construct(4, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, g.N)):
                break
            theta = rt.binary("+", rt.binary("*", rt.binary("-", rt.binary("/", rt.construct(1, i), rt.construct(1, rt.binary("-", g.N, rt.i(1), 1, "int")), 1, "float"), rt.f(0.5), 1, "float"), arc, 1, "float"), jitter, 1, "float")
            distorted = rt.component_wise("clamp", rotateAround__vec2_vec2_float_float(uv, center, theta, aspectRatio), rt.f(0.0), rt.f(1.0), width=2)
            sampleUV = rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.binary("*", distorted, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
            sum[:] = rt.binary("+", sum, rt.texture(_u_inputTex, sampleUV), 4, "float")
        g.fragColor[:] = rt.binary("/", sum, rt.construct(1, g.N), 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
