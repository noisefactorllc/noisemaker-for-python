def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_radius = U.get("radius", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    g.fragColor = rt.construct(4, 0.0)
    def hash22__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.construct(3, rt.f(0.1031), rt.f(0.103), rt.f(0.0973)), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "xx"), rt.swizzle(p3, "yz"), 2, "float"), rt.swizzle(p3, "zy"), 2, "float"), width=2)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradient__vec2(uv):
        uv = rt.copy(uv, "float")
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        tl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1, "float"), 1, "float"), br, 1, "float"), tl, 1, "float"), rt.binary("*", rt.f(2.0), l, 1, "float"), 1, "float"), bl, 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), tr, 1, "float"), bl, 1, "float"), rt.binary("*", rt.f(2.0), b, 1, "float"), 1, "float"), br, 1, "float"))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        hashCoord = globalCoord
        if rt.binary("==", _u_MODE, rt.i(4)):
            hashCoord[:] = rt.binary("*", rt.component_wise("floor", rt.binary("/", globalCoord, rt.f(3.0), 2, "float"), width=2), rt.f(3.0), 2, "float")
        rnd = rt.binary("-", hash22__vec2(rt.binary("+", hashCoord, rt.binary("*", rt.construct(1, _u_seed), rt.f(101.7), 1, "float"), 2, "float")), rt.f(0.5), 2, "float")
        offset = rt.binary("*", rt.binary("*", rnd, rt.f(2.0), 2, "float"), _u_radius, 2, "float")
        grad = rt.construct(2, 0.0)
        gradLen = rt.f(0.0)
        if rt.binary("==", _u_MODE, rt.i(3)):
            grad = lumGradient__vec2(uv)
            gradLen = rt.length(grad)
            perp = rt.construct(2, 0.0)
            if rt.binary(">", gradLen, rt.f(1e-05)):
                perp = rt.binary("/", rt.construct(2, rt.unary("-", rt.swizzle(grad, "y")), rt.swizzle(grad, "x")), gradLen, 2, "float")
                offset[:] = rt.binary("*", rt.dot(offset, perp), perp, 2, "float")
        sampleUV = rt.component_wise("clamp", rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), offset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
        src = rt.texture(_u_inputTex, uv)
        samp = rt.texture(_u_inputTex, sampleUV)
        result = samp
        if rt.binary("==", _u_MODE, rt.i(1)):
            result[:] = rt.component_wise("min", src, samp, width=4)
        else:
            if rt.binary("==", _u_MODE, rt.i(2)):
                result[:] = rt.component_wise("max", src, samp, width=4)
        g.fragColor[:] = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
