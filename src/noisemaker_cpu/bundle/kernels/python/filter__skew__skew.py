def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_skewAmt = U["skewAmt"]
    _u_rotation = U["rotation"]
    _u_wrap = U["wrap"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_renderScale = U["renderScale"]
    g.PI = rt.f(3.14159265359)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        resolution = rt.construct(2, texSize)
        globalPixel = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalPixel, _u_fullResolution, 2, "float")
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        st = globalUV
        st = rt.binary("-", st, rt.f(0.5), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), aspect, 1, "float"))
        angle = rt.binary("/", rt.binary("*", _u_rotation, g.PI, 1, "float"), rt.f(180.0), 1, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        st = rt.matrix_mult(rt.construct(4, c, rt.unary("-", s), s, c), st, 2)
        maxSkew = rt.binary("/", rt.f(512.0), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        effectiveSkewAmt = rt.component_wise("clamp", _u_skewAmt, rt.unary("-", maxSkew), maxSkew, width=1)
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", rt.swizzle(st, "y"), rt.unary("-", effectiveSkewAmt), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), aspect, 1, "float"))
        st = rt.binary("+", st, rt.f(0.5), 2, "float")
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", st, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), resolution, 2, "float")
        wrapMode = rt.construct(1, _u_wrap, base="int")
        if rt.binary("==", wrapMode, rt.i(0)):
            localUV = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        else:
            if rt.binary("==", wrapMode, rt.i(1)):
                localUV = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", localUV, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
            else:
                localUV = rt.component_wise("fract", localUV, width=2)
        g.fragColor = rt.texture(_u_inputTex, localUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
