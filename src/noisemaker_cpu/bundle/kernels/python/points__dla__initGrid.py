def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_gridTex = T["gridTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_frame = U.get("frame", 0)
    _u_decay = U.get("decay", rt.f(0.0))
    _u_anchorDensity = U.get("anchorDensity", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    g.fragColor = rt.construct(4, 0.0)
    def hash21__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "zyx"), rt.f(31.32), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        if _u_resetState:
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        prevGrid = rt.texture(_u_gridTex, uv)
        prev = rt.swizzle(prevGrid, "a")
        prevColor = rt.swizzle(prevGrid, "rgb")
        persistence = rt.binary("-", rt.f(1.0), _u_decay, 1, "float")
        energy = rt.binary("*", prev, persistence, 1, "float")
        color = rt.binary("*", prevColor, persistence, 3, "float")
        energy = rt.component_wise("min", energy, rt.f(3.0), width=1)
        rng = hash21__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        radial = rt.component_wise("smoothstep", rt.f(0.25), rt.f(0.0), rt.length(rt.binary("-", uv, rt.f(0.5), 2, "float")), width=1)
        seedThreshold = rt.binary("-", rt.f(1.0), rt.binary("*", _u_anchorDensity, rt.f(0.1), 1, "float"), 1, "float")
        seedWeight = rt.binary("*", rt.component_wise("step", seedThreshold, rng, width=1), radial, 1, "float")
        strength = rt.f(0.0)
        if (bool(rt.binary(">", seedWeight, rt.f(0.0))) and bool(rt.binary("<", prev, rt.f(0.1)))):
            strength = rt.component_wise("mix", rt.f(0.5), rt.f(1.0), rng, width=1)
            energy = rt.component_wise("max", energy, strength, width=1)
            color[:] = rt.construct(3, strength)
        g.fragColor[:] = rt.construct(4, color, energy)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
