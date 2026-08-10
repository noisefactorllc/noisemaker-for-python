def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_h1 = T["h1"]
    _u_h2 = T["h2"]
    _u_h3 = T["h3"]
    _u_h4 = T["h4"]
    _u_h5 = T["h5"]
    _u_h6 = T["h6"]
    _u_h7 = T["h7"]
    _u_h8 = T["h8"]
    _u_redDelay = U.get("redDelay", rt.f(0.0))
    _u_greenDelay = U.get("greenDelay", rt.f(0.0))
    _u_blueDelay = U.get("blueDelay", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        cur = rt.texture(_u_inputTex, uv)
        slots = rt.new_array(rt.i(9), 4)
        slots[int(rt.i(0))] = cur
        s = rt.construct(4, 0.0)
        s[:] = rt.texture(_u_h1, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(1))].__setitem__(slice(None), s), slots[int(rt.i(1))])[-1])
        s[:] = rt.texture(_u_h2, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(2))].__setitem__(slice(None), s), slots[int(rt.i(2))])[-1])
        s[:] = rt.texture(_u_h3, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(3))].__setitem__(slice(None), s), slots[int(rt.i(3))])[-1])
        s[:] = rt.texture(_u_h4, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(4))].__setitem__(slice(None), s), slots[int(rt.i(4))])[-1])
        s[:] = rt.texture(_u_h5, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(5))].__setitem__(slice(None), s), slots[int(rt.i(5))])[-1])
        s[:] = rt.texture(_u_h6, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(6))].__setitem__(slice(None), s), slots[int(rt.i(6))])[-1])
        s[:] = rt.texture(_u_h7, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(7))].__setitem__(slice(None), s), slots[int(rt.i(7))])[-1])
        s[:] = rt.texture(_u_h8, uv)
        (cur if rt.binary("<", rt.swizzle(s, "a"), rt.f(0.5)) else (slots[int(rt.i(8))].__setitem__(slice(None), s), slots[int(rt.i(8))])[-1])
        dr = rt.component_wise("clamp", _u_redDelay, rt.f(0.0), rt.f(8.0), width=1)
        ir0 = rt.construct(1, rt.component_wise("floor", dr, width=1), base="int")
        ir1 = rt.component_wise("min", rt.binary("+", ir0, rt.i(1), 1, "int"), rt.i(8), width=1)
        rOut = rt.swizzle(rt.component_wise("mix", slots[int(ir0)], slots[int(ir1)], rt.binary("-", dr, rt.construct(1, ir0), 1, "float"), width=4), "r")
        dg = rt.component_wise("clamp", _u_greenDelay, rt.f(0.0), rt.f(8.0), width=1)
        ig0 = rt.construct(1, rt.component_wise("floor", dg, width=1), base="int")
        ig1 = rt.component_wise("min", rt.binary("+", ig0, rt.i(1), 1, "int"), rt.i(8), width=1)
        gOut = rt.swizzle(rt.component_wise("mix", slots[int(ig0)], slots[int(ig1)], rt.binary("-", dg, rt.construct(1, ig0), 1, "float"), width=4), "g")
        db = rt.component_wise("clamp", _u_blueDelay, rt.f(0.0), rt.f(8.0), width=1)
        ib0 = rt.construct(1, rt.component_wise("floor", db, width=1), base="int")
        ib1 = rt.component_wise("min", rt.binary("+", ib0, rt.i(1), 1, "int"), rt.i(8), width=1)
        bOut = rt.swizzle(rt.component_wise("mix", slots[int(ib0)], slots[int(ib1)], rt.binary("-", db, rt.construct(1, ib0), 1, "float"), width=4), "b")
        g.fragColor[:] = rt.construct(4, rOut, gOut, bOut, rt.swizzle(cur, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
