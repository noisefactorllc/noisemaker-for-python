def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_STYLE = U.get("STYLE", 0)
    _u_WRAP = U.get("WRAP", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_amount = U.get("amount", rt.f(0.0))
    _u_ridges = U.get("ridges", 0)
    _u_antialias = U.get("antialias", False)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        uv[:] = rt.binary("-", uv, rt.f(0.5), 2, "float")
        uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), aspectRatio, 1, "float"))
        r = rt.length(uv)
        phase = rt.binary("*", rt.binary("*", rt.binary("*", r, rt.construct(1, _u_ridges), 1, "float"), rt.f(2.0), 1, "float"), rt.f(3.14159265359), 1, "float")
        damping = rt.component_wise("max", rt.f(0.0), rt.binary("-", rt.f(1.0), r, 1, "float"), width=1)
        w = rt.f(0.0)
        x = rt.f(0.0)
        amountGain = rt.f(0.0)
        if rt.binary("<=", _u_amount, rt.f(30.0)):
            w = rt.binary("*", rt.binary("*", rt.binary("*", rt.component_wise("sin", phase, width=1), rt.binary("/", _u_amount, rt.f(100.0), 1, "float"), 1, "float"), rt.f(0.05), 1, "float"), damping, 1, "float")
        else:
            x = rt.binary("/", rt.binary("-", _u_amount, rt.f(30.0), 1, "float"), rt.f(70.0), 1, "float")
            amountGain = rt.binary("+", rt.binary("+", rt.f(0.3), rt.binary("*", rt.f(0.7), x, 1, "float"), 1, "float"), rt.binary("*", x, x, 1, "float"), 1, "float")
            w = rt.binary("*", rt.binary("*", rt.binary("*", rt.component_wise("sin", phase, width=1), amountGain, 1, "float"), rt.f(0.05), 1, "float"), damping, 1, "float")
        rotDelta = rt.f(0.0)
        rDelta = rt.f(0.0)
        if rt.binary("==", _u_STYLE, rt.i(0)):
            rotDelta = w
        else:
            if rt.binary("==", _u_STYLE, rt.i(1)):
                rDelta = w
            else:
                rotDelta = rt.binary("*", w, rt.f(0.5), 1, "float")
                rDelta = rt.binary("*", w, rt.f(0.5), 1, "float")
        dir = (rt.binary("/", uv, r, 2, "float") if rt.binary(">", r, rt.f(0.0)) else rt.construct(2, rt.f(0.0)))
        rot = rt.binary("*", rt.binary("*", rt.binary("*", rotDelta, rt.f(2.0), 1, "float"), rt.f(3.14159265359), 1, "float"), rt.f(0.25), 1, "float")
        s = rt.component_wise("sin", rot, width=1)
        co = rt.component_wise("cos", rot, width=1)
        rotatedDir = rt.matrix_mult(rt.construct(4, co, rt.unary("-", s), s, co), dir, 2)
        uv[:] = rt.binary("*", rotatedDir, rt.binary("+", r, rDelta, 1, "float"), 2, "float")
        uv = rt.assign_swizzle(uv, "x", rt.binary("/", rt.swizzle(uv, "x"), aspectRatio, 1, "float"))
        uv[:] = rt.binary("+", uv, rt.f(0.5), 2, "float")
        if rt.binary("==", _u_WRAP, rt.i(0)):
            uv[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_WRAP, rt.i(1)):
                uv[:] = rt.component_wise("mod", uv, rt.f(1.0), width=2)
            else:
                uv[:] = rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        sampleUV = rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
        dx = rt.construct(2, 0.0)
        dy = rt.construct(2, 0.0)
        col = rt.construct(4, 0.0)
        if _u_antialias:
            dx = rt.dFdx(sampleUV)
            dy = rt.dFdy(sampleUV)
            col = rt.construct(4, rt.f(0.0))
            col[:] = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col[:] = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col[:] = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col[:] = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampleUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            g.fragColor[:] = rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            g.fragColor[:] = rt.texture(_u_inputTex, sampleUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.uses_derivatives = True
