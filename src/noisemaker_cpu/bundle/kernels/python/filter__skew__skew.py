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
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        resolution = rt.construct(2, texSize)
        globalPixel = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        globalUV = rt.binary("/", globalPixel, _u_fullResolution, 2)
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        st = globalUV
        st = rt.binary("-", st, rt.f(0.5), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), aspect, 1))
        angle = rt.binary("/", rt.binary("*", _u_rotation, g.PI, 1), rt.f(180.0), 1)
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        st = rt.binary("*", rt.construct(4, c, rt.unary("-", s), s, c), st, 4)
        maxSkew = rt.binary("/", rt.f(512.0), rt.swizzle(_u_fullResolution, "y"), 1)
        effectiveSkewAmt = rt.component_wise("clamp", _u_skewAmt, rt.unary("-", maxSkew), maxSkew, width=1)
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", rt.swizzle(st, "y"), rt.unary("-", effectiveSkewAmt), 1), 1))
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), aspect, 1))
        st = rt.binary("+", st, rt.f(0.5), 2)
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", st, _u_fullResolution, 2), _u_tileOffset, 2), resolution, 2)
        wrapMode = rt.construct(1, _u_wrap)
        if rt.binary("==", wrapMode, rt.i(0)):
            localUV = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        else:
            if rt.binary("==", wrapMode, rt.i(1)):
                localUV = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", localUV, rt.f(1.0), 2), rt.f(2.0), width=2), rt.f(1.0), 2), width=2)
            else:
                localUV = rt.component_wise("fract", localUV, width=2)
        g.fragColor = rt.texture(_u_inputTex, localUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
