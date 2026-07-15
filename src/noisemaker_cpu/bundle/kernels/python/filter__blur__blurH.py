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
    _u_radiusX = U["radiusX"]
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
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2)
        radius = rt.construct(1, rt.binary("*", _u_radiusX, _u_renderScale, 1))
        if rt.binary("<=", radius, rt.i(0)):
            g.fragColor = rt.texture(_u_inputTex, uv)
            return
        sigma = rt.binary("/", radius, rt.f(3.0), 1)
        sigma2 = rt.binary("*", sigma, sigma, 1)
        sum = rt.construct(4, rt.f(0.0))
        weightSum = rt.f(0.0)
        i = rt.unary("-", radius)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<=", i, radius)):
                break
            x = i
            weight = rt.component_wise("exp", rt.binary("/", rt.unary("-", rt.binary("*", x, x, 1)), rt.binary("*", rt.f(2.0), sigma2, 1), 1), width=1)
            offset = rt.construct(2, rt.binary("*", i, rt.swizzle(texelSize, "x"), 1), rt.f(0.0))
            sum = rt.binary("+", sum, rt.binary("*", rt.texture(_u_inputTex, rt.binary("+", uv, offset, 2)), weight, 4), 4)
            weightSum = rt.binary("+", weightSum, weight, 1)
        g.fragColor = rt.binary("/", sum, weightSum, 4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
