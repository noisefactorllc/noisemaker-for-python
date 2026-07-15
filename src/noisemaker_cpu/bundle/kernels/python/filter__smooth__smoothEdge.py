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
    _u_smoothType = U["smoothType"]
    _u_threshold = U["threshold"]
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114))
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def luminance__vec3(rgb):
        rgb = rt.copy(rgb)
        return rt.dot(rgb, g.LUMA_WEIGHTS)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        if rt.binary("==", _u_smoothType, rt.i(0)):
            g.fragColor = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
            return
        maxCoord = rt.binary("-", texSize, rt.i(1), 2)
        L = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, coord, rt.i(0)), "rgb"))
        Ln = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(0), rt.unary("-", rt.i(1))), 2), cpu_ivec2__float(rt.i(0)), maxCoord, width=2), rt.i(0)), "rgb"))
        Ls = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), cpu_ivec2__float(rt.i(0)), maxCoord, width=2), rt.i(0)), "rgb"))
        Lw = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.i(0)), 2), cpu_ivec2__float(rt.i(0)), maxCoord, width=2), rt.i(0)), "rgb"))
        Le = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), cpu_ivec2__float(rt.i(0)), maxCoord, width=2), rt.i(0)), "rgb"))
        edgeH = rt.component_wise("step", _u_threshold, rt.component_wise("max", rt.component_wise("abs", rt.binary("-", L, Ln, 1), width=1), rt.component_wise("abs", rt.binary("-", L, Ls, 1), width=1), width=1), width=1)
        edgeV = rt.component_wise("step", _u_threshold, rt.component_wise("max", rt.component_wise("abs", rt.binary("-", L, Lw, 1), width=1), rt.component_wise("abs", rt.binary("-", L, Le, 1), width=1), width=1), width=1)
        g.fragColor = rt.construct(4, edgeH, edgeV, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
