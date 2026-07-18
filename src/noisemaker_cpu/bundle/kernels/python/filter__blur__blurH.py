def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_radiusX = U.get("radiusX", rt.f(0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.PI = rt.f(3.14159265359)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2, "float")
        radius = rt.construct(1, rt.binary("*", _u_radiusX, _u_renderScale, 1, "float"), base="int")
        if rt.binary("<=", radius, rt.i(0)):
            g.fragColor[:] = rt.texture(_u_inputTex, uv)
            return
        sigma = rt.binary("/", rt.construct(1, radius), rt.f(3.0), 1, "float")
        sigma2 = rt.binary("*", sigma, sigma, 1, "float")
        sum = rt.construct(4, rt.f(0.0))
        weightSum = rt.f(0.0)
        i = rt.unary("-", radius)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", i, radius)):
                break
            x = rt.construct(1, i)
            weight = rt.component_wise("exp", rt.binary("/", rt.unary("-", rt.binary("*", x, x, 1, "float")), rt.binary("*", rt.f(2.0), sigma2, 1, "float"), 1, "float"), width=1)
            offset = rt.construct(2, rt.binary("*", rt.construct(1, i), rt.swizzle(texelSize, "x"), 1, "float"), rt.f(0.0))
            sum[:] = rt.binary("+", sum, rt.binary("*", rt.texture(_u_inputTex, rt.binary("+", uv, offset, 2, "float")), weight, 4, "float"), 4, "float")
            weightSum = rt.binary("+", weightSum, weight, 1, "float")
        g.fragColor[:] = rt.binary("/", sum, weightSum, 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
