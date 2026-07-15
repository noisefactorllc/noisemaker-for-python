def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U["MODE"]
    _u_inputTex = T["inputTex"]
    _u_smearTex = T["smearTex"]
    _u_resolution = U["resolution"]
    _u_sharpness = U["sharpness"]
    def tent3x3__vec2(uv):
        uv = rt.copy(uv)
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        sum = rt.construct(3, rt.f(0.0))
        wsum = rt.f(0.0)
        dy = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dy = rt.binary("+", dy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", dy, rt.i(1))):
                break
            dx = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    dx = rt.binary("+", dx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", dx, rt.i(1))):
                    break
                w = rt.binary("*", (rt.f(2.0) if rt.binary("==", dx, rt.i(0)) else rt.f(1.0)), (rt.f(2.0) if rt.binary("==", dy, rt.i(0)) else rt.f(1.0)), 1, "float")
                sum = rt.binary("+", sum, rt.binary("*", rt.swizzle(rt.texture(_u_smearTex, rt.binary("+", uv, rt.binary("*", rt.construct(2, rt.construct(1, dx), rt.construct(1, dy)), px, 2, "float"), 2, "float")), "rgb"), w, 3, "float"), 3, "float")
                wsum = rt.binary("+", wsum, w, 1, "float")
        return rt.binary("/", sum, wsum, 3, "float")
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        c = rt.swizzle(rt.texture(_u_smearTex, uv), "rgb")
        tent = tent3x3__vec2(uv)
        sharpened = rt.binary("+", c, rt.binary("*", rt.binary("-", c, tent, 3, "float"), rt.binary("/", _u_sharpness, rt.f(33.0), 1, "float"), 3, "float"), 3, "float")
        g.fragColor = rt.construct(4, rt.component_wise("clamp", sharpened, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
