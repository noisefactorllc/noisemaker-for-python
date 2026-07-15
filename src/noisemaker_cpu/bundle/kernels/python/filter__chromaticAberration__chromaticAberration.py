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
    _u_aberrationAmt = U["aberrationAmt"]
    _u_passthru = U["passthru"]
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1), rt.binary("-", value, inMin, 1), 1), rt.binary("-", inMax, inMin, 1), 1), 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        globalAspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        diff = rt.binary("-", rt.construct(2, rt.binary("*", rt.f(0.5), globalAspect, 1), rt.f(0.5)), rt.construct(2, rt.binary("*", rt.swizzle(globalUV, "x"), globalAspect, 1), rt.swizzle(globalUV, "y")), 2)
        centerDist = rt.length(diff)
        aberrationOffset = rt.binary("*", rt.binary("*", rt.binary("*", map__float_float_float_float_float(_u_aberrationAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.05)), centerDist, 1), rt.f(3.14159265359), 1), rt.f(0.5), 1)
        redOffset = rt.component_wise("mix", rt.component_wise("clamp", rt.binary("+", rt.swizzle(uv, "x"), aberrationOffset, 1), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(uv, "x"), rt.swizzle(uv, "x"), width=1)
        red = rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.construct(2, redOffset, rt.swizzle(uv, "y")), _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        green = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        blueOffset = rt.component_wise("mix", rt.swizzle(uv, "x"), rt.component_wise("clamp", rt.binary("-", rt.swizzle(uv, "x"), aberrationOffset, 1), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(uv, "x"), width=1)
        blue = rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.construct(2, blueOffset, rt.swizzle(uv, "y")), _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        aberrated = rt.construct(3, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"))
        edges = rt.binary("-", aberrated, rt.swizzle(green, "rgb"), 3)
        original = rt.binary("*", rt.swizzle(green, "rgb"), map__float_float_float_float_float(_u_passthru, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0)), 3)
        g.fragColor = rt.construct(4, rt.component_wise("min", rt.binary("+", edges, original, 3), rt.f(1.0), width=3), rt.swizzle(green, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
