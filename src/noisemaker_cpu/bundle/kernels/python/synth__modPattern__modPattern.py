def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_shape1 = U.get("shape1", 0)
    _u_scale1 = U.get("scale1", rt.f(0.0))
    _u_repeat1 = U.get("repeat1", rt.f(0.0))
    _u_shape2 = U.get("shape2", 0)
    _u_scale2 = U.get("scale2", rt.f(0.0))
    _u_repeat2 = U.get("repeat2", rt.f(0.0))
    _u_shape3 = U.get("shape3", 0)
    _u_scale3 = U.get("scale3", rt.f(0.0))
    _u_repeat3 = U.get("repeat3", rt.f(0.0))
    _u_blend = U.get("blend", 0)
    _u_smoothing = U.get("smoothing", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_animMode = U.get("animMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def shape__int_vec2(shapeIndex, p):
        p = rt.copy(p, "float")
        v = rt.f(0.0)
        if rt.binary("<", shapeIndex, rt.i(1)):
            v = rt.component_wise("max", rt.swizzle(p, "x"), rt.swizzle(p, "y"), width=1)
        else:
            if rt.binary("<", shapeIndex, rt.i(2)):
                v = rt.component_wise("min", rt.swizzle(p, "x"), rt.swizzle(p, "y"), width=1)
            else:
                v = rt.component_wise("abs", rt.binary("-", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), width=1)
        return v
    def smoothFract__float(x):
        f = rt.component_wise("fract", x, width=1)
        edgeWidth = rt.binary("*", _u_smoothing, rt.f(0.01), 1, "float")
        if rt.binary(">", f, rt.binary("-", rt.f(1.0), edgeWidth, 1, "float")):
            return rt.component_wise("smoothstep", rt.f(0.0), edgeWidth, rt.binary("-", rt.f(1.0), f, 1, "float"), width=1)
        return f
    def smoothFract__vec2(v):
        v = rt.copy(v, "float")
        return rt.construct(2, smoothFract__float(rt.swizzle(v, "x")), smoothFract__float(rt.swizzle(v, "y")))
    def smoothFract__vec3(v):
        v = rt.copy(v, "float")
        return rt.construct(3, smoothFract__float(rt.swizzle(v, "x")), smoothFract__float(rt.swizzle(v, "y")), smoothFract__float(rt.swizzle(v, "z")))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.binary("-", globalCoord, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2, "float"), rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 2, "float")
        spd = rt.component_wise("floor", _u_speed, width=1)
        anim = rt.binary("*", _u_time, spd, 1, "float")
        s1 = rt.binary("-", rt.f(20.1), _u_scale1, 1, "float")
        p = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", uv, s1, 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        osc1 = rt.f(0.0)
        if rt.binary("==", _u_animMode, rt.i(1)):
            osc1 = rt.binary("*", rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), width=1), rt.f(0.03), 1, "float")
            p[:] = rt.binary("+", p, rt.construct(2, osc1, rt.f(0.0)), 2, "float")
        n1 = shape__int_vec2(_u_shape1, p)
        phase1 = (anim if rt.binary("==", _u_animMode, rt.i(2)) else rt.f(0.0))
        phase2 = (anim if rt.binary("==", _u_animMode, rt.i(2)) else rt.f(0.0))
        phase3 = (anim if rt.binary("==", _u_animMode, rt.i(2)) else rt.f(0.0))
        s2 = rt.binary("-", rt.f(10.1), _u_scale2, 1, "float")
        p[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", p, s2, 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        osc2 = rt.f(0.0)
        if rt.binary("==", _u_animMode, rt.i(1)):
            osc2 = rt.binary("*", rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), width=1), rt.f(0.07), 1, "float")
            p[:] = rt.binary("+", p, rt.construct(2, rt.f(0.0), osc2), 2, "float")
        n2 = shape__int_vec2(_u_shape2, p)
        val = rt.f(0.0)
        if rt.binary("<", _u_blend, rt.i(1)):
            val = rt.component_wise("fract", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", n1, _u_repeat1, 1, "float"), phase1, 1, "float"), rt.binary("*", n2, _u_repeat2, 1, "float"), 1, "float"), phase2, 1, "float"), width=1)
        else:
            val = smoothFract__float(rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", n1, _u_repeat1, 1, "float"), phase1, 1, "float"), rt.binary("*", n2, _u_repeat2, 1, "float"), 1, "float"), phase2, 1, "float"))
        s3 = rt.binary("-", rt.f(6.1), _u_scale3, 1, "float")
        p[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", p, s3, 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        osc3 = rt.f(0.0)
        if rt.binary("==", _u_animMode, rt.i(1)):
            osc3 = rt.binary("*", rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), width=1), rt.f(0.15), 1, "float")
            p[:] = rt.binary("+", p, rt.construct(2, rt.unary("-", osc3), rt.f(0.0)), 2, "float")
        n3 = shape__int_vec2(_u_shape3, p)
        shift = (anim if rt.binary("==", _u_animMode, rt.i(0)) else rt.f(0.0))
        color = rt.construct(3, 0.0)
        if rt.binary("<", _u_blend, rt.i(1)):
            color[:] = smoothFract__vec3(rt.construct(3, rt.component_wise("fract", rt.binary("+", rt.binary("+", rt.binary("+", val, rt.binary("*", n3, _u_repeat3, 1, "float"), 1, "float"), phase3, 1, "float"), shift, 1, "float"), width=1)))
        else:
            if rt.binary("<", _u_blend, rt.i(2)):
                color[:] = rt.construct(3, rt.component_wise("max", val, smoothFract__float(rt.binary("+", rt.binary("+", rt.binary("*", n3, _u_repeat3, 1, "float"), phase3, 1, "float"), shift, 1, "float")), width=1))
            else:
                if rt.binary("<", _u_blend, rt.i(3)):
                    color[:] = rt.construct(3, rt.component_wise("mix", val, smoothFract__float(rt.binary("+", rt.binary("+", rt.binary("*", n3, _u_repeat3, 1, "float"), phase3, 1, "float"), shift, 1, "float")), rt.f(0.5), width=1))
                else:
                    color[:] = smoothFract__vec3(rt.construct(3, rt.binary("+", rt.binary("*", n1, _u_repeat1, 1, "float"), phase1, 1, "float"), rt.binary("+", rt.binary("*", n2, _u_repeat2, 1, "float"), phase2, 1, "float"), rt.binary("+", rt.binary("+", rt.binary("*", n3, _u_repeat3, 1, "float"), phase3, 1, "float"), shift, 1, "float")))
        g.fragColor[:] = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
