def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_strength = U["strength"]
    _u_aspectLens = U["aspectLens"]
    _u_wrap = U["wrap"]
    _u_rotation = U["rotation"]
    _u_antialias = U["antialias"]
    def rotate2D__vec2_float_float(st, rot, aspectRatio):
        st = rt.copy(st)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), aspectRatio, 1, "float"))
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.f(0.5), aspectRatio, 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st = rt.binary("+", st, rt.construct(2, rt.binary("*", rt.f(0.5), aspectRatio, 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), aspectRatio, 1, "float"))
        return st
    def main__void():
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        uv = rotate2D__vec2_float_float(uv, rt.binary("/", _u_rotation, rt.f(180.0), 1, "float"), aspectRatio)
        intensity = rt.binary("*", _u_strength, rt.unary("-", rt.f(0.01)), 1, "float")
        uv = rt.binary("-", uv, rt.f(0.5), 2, "float")
        if _u_aspectLens:
            uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), aspectRatio, 1, "float"))
        r = rt.length(uv)
        effect = rt.component_wise("pow", r, rt.binary("-", rt.f(1.0), intensity, 1, "float"), width=1)
        uv = rt.binary("*", rt.normalize(uv), effect, 2, "float")
        if _u_aspectLens:
            uv = rt.assign_swizzle(uv, "x", rt.binary("/", rt.swizzle(uv, "x"), aspectRatio, 1, "float"))
        uv = rt.binary("+", uv, rt.f(0.5), 2, "float")
        if rt.binary("==", _u_wrap, rt.i(0)):
            uv = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                uv = rt.component_wise("mod", uv, rt.f(1.0), width=2)
            else:
                uv = rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        uv = rotate2D__vec2_float_float(uv, rt.binary("/", rt.unary("-", _u_rotation), rt.f(180.0), 1, "float"), aspectRatio)
        sampleUV = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), width=2)
        if _u_antialias:
            dx = rt.component_wise("dFdx", sampleUV, width=2)
            dy = rt.component_wise("dFdy", sampleUV, width=2)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            g.fragColor = rt.texture(_u_inputTex, sampleUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
