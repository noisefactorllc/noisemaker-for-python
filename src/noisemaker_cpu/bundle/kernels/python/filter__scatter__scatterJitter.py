def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U["MODE"]
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_radius = U["radius"]
    _u_seed = U["seed"]
    def hash22__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.construct(3, rt.f(0.1031), rt.f(0.1030), rt.f(0.0973)), 3), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3)), 3)
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "xx"), rt.swizzle(p3, "yz"), 2), rt.swizzle(p3, "zy"), 2), width=2)
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradient__vec2(uv):
        uv = rt.copy(uv)
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2)
        tl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2), 2)), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2), 2)), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2), 2)), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2), 2)), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2), 2)), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1), 1), br, 1), tl, 1), rt.binary("*", rt.f(2.0), l, 1), 1), bl, 1), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1), 1), tr, 1), bl, 1), rt.binary("*", rt.f(2.0), b, 1), 1), br, 1))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        hashCoord = globalCoord
        if rt.binary("==", _u_MODE, rt.i(4)):
            hashCoord = rt.binary("*", rt.component_wise("floor", rt.binary("/", globalCoord, rt.f(3.0), 2), width=2), rt.f(3.0), 2)
        rnd = rt.binary("-", hash22__vec2(rt.binary("+", hashCoord, rt.binary("*", _u_seed, rt.f(101.7), 1), 2)), rt.f(0.5), 2)
        offset = rt.binary("*", rt.binary("*", rnd, rt.f(2.0), 2), _u_radius, 2)
        if rt.binary("==", _u_MODE, rt.i(3)):
            grad = lumGradient__vec2(uv)
            gradLen = rt.length(grad)
            if rt.binary(">", gradLen, rt.f(1e-5)):
                perp = rt.binary("/", rt.construct(2, rt.unary("-", rt.swizzle(grad, "y")), rt.swizzle(grad, "x")), gradLen, 2)
                offset = rt.binary("*", rt.dot(offset, perp), perp, 2)
        sampleUV = rt.component_wise("clamp", rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), offset, 2), _u_resolution, 2), rt.f(0.0), rt.f(1.0), width=2)
        src = rt.texture(_u_inputTex, uv)
        samp = rt.texture(_u_inputTex, sampleUV)
        result = samp
        if rt.binary("==", _u_MODE, rt.i(1)):
            result = rt.component_wise("min", src, samp, width=4)
        else:
            if rt.binary("==", _u_MODE, rt.i(2)):
                result = rt.component_wise("max", src, samp, width=4)
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
