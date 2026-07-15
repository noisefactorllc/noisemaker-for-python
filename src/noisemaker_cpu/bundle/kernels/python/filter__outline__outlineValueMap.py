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
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def srgbToLinear__float(value):
        return (rt.binary("/", value, rt.f(12.92), 1) if rt.binary("<=", value, rt.f(0.04045)) else rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1), rt.f(1.055), 1), rt.f(2.4), width=1))
    def srgbToLinear__vec3(value):
        value = rt.copy(value)
        return rt.construct(3, srgbToLinear__float(rt.swizzle(value, "r")), srgbToLinear__float(rt.swizzle(value, "g")), srgbToLinear__float(rt.swizzle(value, "b")))
    def cubeRoot__float(value):
        return (rt.unary("-", rt.component_wise("pow", rt.unary("-", value), rt.binary("/", rt.f(1.0), rt.f(3.0), 1), width=1)) if rt.binary("<", value, rt.f(0.0)) else rt.component_wise("pow", value, rt.binary("/", rt.f(1.0), rt.f(3.0), 1), width=1))
    def oklabLComponent__vec3(rgb):
        rgb = rt.copy(rgb)
        linear = srgbToLinear__vec3(rt.component_wise("clamp", rgb, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.4121656120), rt.swizzle(linear, "r"), 1), rt.binary("*", rt.f(0.5362752080), rt.swizzle(linear, "g"), 1), 1), rt.binary("*", rt.f(0.0514575653), rt.swizzle(linear, "b"), 1), 1)
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2118591070), rt.swizzle(linear, "r"), 1), rt.binary("*", rt.f(0.6807189584), rt.swizzle(linear, "g"), 1), 1), rt.binary("*", rt.f(0.1074065790), rt.swizzle(linear, "b"), 1), 1)
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), rt.swizzle(linear, "r"), 1), rt.binary("*", rt.f(0.2818474174), rt.swizzle(linear, "g"), 1), 1), rt.binary("*", rt.f(0.6302613616), rt.swizzle(linear, "b"), 1), 1)
        lC = cubeRoot__float(rt.component_wise("max", l, rt.f(1e-9), width=1))
        mC = cubeRoot__float(rt.component_wise("max", m, rt.f(1e-9), width=1))
        sC = cubeRoot__float(rt.component_wise("max", s, rt.f(1e-9), width=1))
        return rt.component_wise("clamp", rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), lC, 1), rt.binary("*", rt.f(0.7936177850), mC, 1), 1), rt.binary("*", rt.f(0.0040720468), sC, 1), 1), rt.f(0.0), rt.f(1.0), width=1)
    def valueMapComponent__vec4(texel):
        texel = rt.copy(texel)
        spread = rt.component_wise("max", rt.component_wise("abs", rt.binary("-", rt.swizzle(texel, "r"), rt.swizzle(texel, "g"), 1), width=1), rt.component_wise("max", rt.component_wise("abs", rt.binary("-", rt.swizzle(texel, "r"), rt.swizzle(texel, "b"), 1), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(texel, "g"), rt.swizzle(texel, "b"), 1), width=1), width=1), width=1)
        if rt.binary("<", spread, rt.f(1e-5)):
            return rt.component_wise("clamp", rt.swizzle(texel, "r"), rt.f(0.0), rt.f(1.0), width=1)
        return oklabLComponent__vec3(rt.swizzle(texel, "rgb"))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        dimensions = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.binary("-", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.f(0.5)), 2), rt.construct(2, rt.component_wise("max", rt.swizzle(dimensions, "x"), rt.i(1), width=1), rt.component_wise("max", rt.swizzle(dimensions, "y"), rt.i(1), width=1)), 2)
        texel = rt.texture(_u_inputTex, uv)
        value = valueMapComponent__vec4(texel)
        g.fragColor = rt.construct(4, value, value, value, rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
