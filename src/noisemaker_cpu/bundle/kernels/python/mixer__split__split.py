def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_position = U.get("position", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_softness = U.get("softness", rt.f(0.0))
    _u_invert = U.get("invert", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        centered = rt.binary("*", rt.binary("-", globalUV, rt.f(0.5), 2, "float"), rt.f(2.0), 2, "float")
        centered = rt.assign_swizzle(centered, "x", rt.binary("*", rt.swizzle(centered, "x"), aspect, 1, "float"))
        rad = rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        c = rt.component_wise("cos", rad, width=1)
        s = rt.component_wise("sin", rad, width=1)
        rotated = rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(centered, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(centered, "y"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(centered, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(centered, "y"), c, 1, "float"), 1, "float"))
        extent = rt.binary("+", rt.binary("+", rt.binary("*", aspect, rt.component_wise("abs", s, width=1), 1, "float"), rt.component_wise("abs", c, width=1), 1, "float"), _u_softness, 1, "float")
        animPos = _u_position
        flipCycle = False
        cycle = rt.f(0.0)
        t = rt.f(0.0)
        if rt.binary(">", _u_speed, rt.f(0.0)):
            cycle = rt.binary("*", rt.binary("*", _u_time, _u_speed, 1, "float"), rt.f(2.0), 1, "float")
            t = rt.component_wise("fract", cycle, width=1)
            flipCycle = rt.binary("==", rt.component_wise("mod", rt.component_wise("floor", cycle, width=1), rt.f(2.0), width=1), rt.f(1.0))
            animPos = rt.binary("-", rt.binary("*", rt.binary("*", t, extent, 1, "float"), rt.f(2.0), 1, "float"), extent, 1, "float")
        d = rt.binary("-", rt.swizzle(rotated, "y"), animPos, 1, "float")
        halfSoft = rt.component_wise("max", rt.binary("*", _u_softness, rt.f(0.5), 1, "float"), rt.f(0.001), width=1)
        mask = rt.component_wise("smoothstep", rt.unary("-", halfSoft), halfSoft, d, width=1)
        if rt.binary("!=", rt.binary("==", _u_invert, rt.i(1)), flipCycle):
            mask = rt.binary("-", rt.f(1.0), mask, 1, "float")
        color = rt.component_wise("mix", colorA, colorB, mask, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
