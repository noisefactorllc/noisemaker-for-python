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
    _u_time = U.get("time", rt.f(0.0))
    _u_strength = U.get("strength", rt.f(0.0))
    _u_speed = U.get("speed", 0)
    _u_aspectLens = U.get("aspectLens", False)
    _u_wrap = U.get("wrap", 0)
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_antialias = U.get("antialias", False)
    g.fragColor = rt.construct(4, 0.0)
    def rotate2D__vec2_float_float(st, rot, aspectRatio):
        st = rt.copy(st, "float")
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
        uv = rt.binary("-", uv, rt.f(0.5), 2, "float")
        if _u_aspectLens:
            uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), aspectRatio, 1, "float"))
        r = rt.length(uv)
        a = rt.component_wise("atan", rt.swizzle(uv, "y"), rt.swizzle(uv, "x"), width=1)
        spiralAmt = rt.binary("*", rt.binary("*", _u_strength, rt.f(0.05), 1, "float"), r, 1, "float")
        a = rt.binary("+", a, rt.binary("-", spiralAmt, rt.binary("*", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.construct(1, _u_speed), 1, "float"), rt.component_wise("sign", _u_strength, width=1), 1, "float"), 1, "float"), 1, "float")
        uv = rt.binary("*", rt.construct(2, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1)), r, 2, "float")
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
        sampleUV = rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
        dx = rt.construct(2, 0.0)
        dy = rt.construct(2, 0.0)
        col = rt.construct(4, 0.0)
        if _u_antialias:
            dx = rt.dFdx(sampleUV)
            dy = rt.dFdy(sampleUV)
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
run_pixel.uses_derivatives = True
