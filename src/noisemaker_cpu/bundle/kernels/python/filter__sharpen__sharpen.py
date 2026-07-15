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
    _u_amount = U["amount"]
    _u_renderScale = U["renderScale"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        resolution = rt.construct(2, texSize)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        texelSize = rt.binary("/", rt.f(1.0), resolution, 2)
        origColor = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        kernel = rt.f(0.0)
        kernel[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(1))] = rt.f(0.0)
        kernel[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(3))] = rt.f(0.0)
        kernel[int(rt.i(4))] = rt.f(5.0)
        kernel[int(rt.i(5))] = rt.f(0.0)
        kernel[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(7))] = rt.f(0.0)
        kernel[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        offsets = rt.construct(2, 0.0)
        offsets[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.unary("-", rt.swizzle(texelSize, "y")))
        offsets[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(texelSize, "y")))
        offsets[int(rt.i(2))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.unary("-", rt.swizzle(texelSize, "y")))
        offsets[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.f(0.0))
        offsets[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        offsets[int(rt.i(5))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.f(0.0))
        offsets[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.swizzle(texelSize, "y"))
        offsets[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.swizzle(texelSize, "y"))
        offsets[int(rt.i(8))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.swizzle(texelSize, "y"))
        conv = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            texSample = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", rt.binary("*", offsets[int(i)], _u_amount, 1), _u_renderScale, 1), 2), _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2)), "rgb")
            conv = rt.binary("+", conv, rt.binary("*", texSample, kernel[int(i)], 3), 3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", conv, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(origColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
