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
    def desaturate__vec3(color):
        color = rt.copy(color)
        avg = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1), 1), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1), 1)
        return rt.construct(3, avg)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2)
        localUV = rt.binary("*", rt.swizzle(ctx.frag_coord, "xy"), texelSize, 2)
        radiusPixels = rt.binary("*", _u_amount, _u_renderScale, 1)
        radiusPixels = rt.component_wise("min", radiusPixels, rt.f(256.0), width=1)
        color = rt.texture(_u_inputTex, localUV)
        center = desaturate__vec3(rt.swizzle(color, "rgb"))
        right = desaturate__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", localUV, rt.binary("*", rt.construct(2, radiusPixels, rt.f(0.0)), texelSize, 2), 2)), "rgb"))
        bottom = desaturate__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", localUV, rt.binary("*", rt.construct(2, rt.f(0.0), radiusPixels), texelSize, 2), 2)), "rgb"))
        dx = rt.binary("-", center, right, 3)
        dy = rt.binary("-", center, bottom, 3)
        dist = rt.binary("*", rt.distance(dx, dy), rt.f(2.5), 1)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", rt.binary("*", rt.swizzle(color, "rgb"), dist, 3), rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
