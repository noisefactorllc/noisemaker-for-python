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
    _u_channel = U.get("channel", 0)
    _u_scale = U.get("scale", rt.f(0.0))
    _u_offset = U.get("offset", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", rt.binary("-", rt.swizzle(ctx.frag_coord, "xy"), rt.f(0.5), 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        c = rt.texture(_u_inputTex, st)
        v = rt.f(0.0)
        if rt.binary("==", _u_channel, rt.i(0)):
            v = rt.swizzle(c, "r")
        else:
            if rt.binary("==", _u_channel, rt.i(1)):
                v = rt.swizzle(c, "g")
            else:
                if rt.binary("==", _u_channel, rt.i(2)):
                    v = rt.swizzle(c, "b")
                else:
                    v = rt.swizzle(c, "a")
        v = rt.component_wise("fract", rt.binary("+", rt.binary("*", v, _u_scale, 1, "float"), _u_offset, 1, "float"), width=1)
        g.fragColor[:] = rt.construct(4, rt.construct(3, v), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
