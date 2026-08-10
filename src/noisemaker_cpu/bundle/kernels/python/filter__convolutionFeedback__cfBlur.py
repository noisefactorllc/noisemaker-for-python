def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_blurRadius = U.get("blurRadius", 0)
    _u_blurAmount = U.get("blurAmount", rt.f(0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        scaledRadius = rt.construct(1, rt.binary("*", rt.construct(1, _u_blurRadius), _u_renderScale, 1, "float"), base="int")
        if (bool(rt.binary("<=", scaledRadius, rt.i(0))) or bool(rt.binary("<=", _u_blurAmount, rt.f(0.0)))):
            g.fragColor[:] = center
            return
        sigma = rt.binary("/", rt.construct(1, scaledRadius), rt.f(2.0), 1, "float")
        sigma2 = rt.binary("*", sigma, sigma, 1, "float")
        sum = rt.construct(3, rt.f(0.0))
        weightSum = rt.f(0.0)
        ky = rt.unary("-", scaledRadius)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                ky = rt.binary("+", ky, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", ky, scaledRadius)):
                break
            kx = rt.unary("-", scaledRadius)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    kx = rt.binary("+", kx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", kx, scaledRadius)):
                    break
                samplePos = rt.binary("+", coord, rt.construct(2, kx, ky, base="int"), 2, "int")
                samplePos[:] = rt.component_wise("clamp", samplePos, rt.construct(2, rt.i(0), base="int"), rt.binary("-", texSize, rt.i(1), 2, "int"), width=2)
                dist2 = rt.construct(1, rt.binary("+", rt.binary("*", kx, kx, 1, "int"), rt.binary("*", ky, ky, 1, "int"), 1, "int"))
                weight = rt.component_wise("exp", rt.binary("/", rt.unary("-", dist2), rt.binary("*", rt.f(2.0), sigma2, 1, "float"), 1, "float"), width=1)
                texSample = rt.texel_fetch(_u_inputTex, samplePos, rt.i(0))
                sum[:] = rt.binary("+", sum, rt.binary("*", rt.swizzle(texSample, "rgb"), weight, 3, "float"), 3, "float")
                weightSum = rt.binary("+", weightSum, weight, 1, "float")
        blurred = rt.binary("/", sum, weightSum, 3, "float")
        result = rt.component_wise("mix", rt.swizzle(center, "rgb"), blurred, _u_blurAmount, width=3)
        g.fragColor[:] = rt.construct(4, result, rt.swizzle(center, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
