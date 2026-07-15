def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_shape = U["shape"]
    _u_speed = U["speed"]
    _u_rotation = U["rotation"]
    _u_scale = U["scale"]
    _u_center = U["center"]
    _u_aspectLens = U["aspectLens"]
    _u_antialias = U["antialias"]
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def polygonShape__vec2_int(uv, sides):
        uv = rt.copy(uv)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(uv, "x"), rt.swizzle(uv, "y"), width=1), g.PI, 1)
        r = rt.binary("/", g.TAU, sides, 1)
        return rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1), 1), width=1), r, 1), a, 1), width=1), rt.length(uv), 1)
    def smod__vec2_float(v, m):
        v = rt.copy(v)
        return rt.binary("*", m, rt.binary("-", rt.binary("-", rt.f(0.75), rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", v, width=2), rt.f(0.5), 2), width=2), 2), rt.f(0.25), 2), 2)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        centered = rt.binary("-", uv, rt.f(0.5), 2)
        aspectRatio = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        if _u_aspectLens:
            centered = rt.assign_swizzle(centered, "x", rt.binary("*", rt.swizzle(centered, "x"), aspectRatio, 1))
        a = rt.component_wise("atan", rt.swizzle(centered, "y"), rt.swizzle(centered, "x"), width=1)
        r = rt.f(0.0)
        if rt.binary("==", _u_shape, rt.i(0)):
            r = rt.length(centered)
        else:
            if rt.binary("==", _u_shape, rt.i(1)):
                r = polygonShape__vec2_int(rt.binary("*", centered, rt.f(2.0), 2), rt.i(3))
            else:
                if rt.binary("==", _u_shape, rt.i(2)):
                    p = rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", centered, centered, 2), centered, 2), centered, 2), centered, 2), centered, 2), centered, 2), centered, 2)
                    r = rt.component_wise("pow", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1), rt.binary("/", rt.f(1.0), rt.f(8.0), 1), width=1)
                else:
                    if rt.binary("==", _u_shape, rt.i(3)):
                        r = polygonShape__vec2_int(rt.binary("*", centered, rt.f(2.0), 2), rt.i(4))
                    else:
                        if rt.binary("==", _u_shape, rt.i(4)):
                            r = polygonShape__vec2_int(rt.binary("*", centered, rt.f(2.0), 2), rt.i(6))
                        else:
                            r = polygonShape__vec2_int(rt.binary("*", centered, rt.f(2.0), 2), rt.i(8))
        r = rt.binary("-", r, rt.binary("*", _u_scale, rt.f(0.15), 1), 1)
        tunnelCoords = smod__vec2_float(rt.construct(2, rt.binary("+", rt.binary("/", rt.f(0.3), r, 1), rt.binary("*", _u_time, _u_speed, 1), 1), rt.binary("+", rt.binary("/", a, g.PI, 1), rt.binary("*", _u_time, _u_rotation, 1), 1)), rt.f(1.0))
        color = rt.construct(4, 0.0)
        if _u_antialias:
            dx = rt.component_wise("dFdx", tunnelCoords, width=2)
            dy = rt.component_wise("dFdy", tunnelCoords, width=2)
            color = rt.construct(4, rt.f(0.0))
            color = rt.binary("+", color, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", tunnelCoords, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2), 2)), 4)
            color = rt.binary("+", color, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", tunnelCoords, rt.binary("*", dx, rt.f(0.125), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2), 2)), 4)
            color = rt.binary("+", color, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", tunnelCoords, rt.binary("*", dx, rt.f(0.375), 2), 2), rt.binary("*", dy, rt.f(0.125), 2), 2)), 4)
            color = rt.binary("+", color, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", tunnelCoords, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2), 2), rt.binary("*", dy, rt.f(0.375), 2), 2)), 4)
            color = rt.binary("*", color, rt.f(0.25), 4)
        else:
            color = rt.texture(_u_inputTex, tunnelCoords)
        if rt.binary("!=", _u_center, rt.f(0.0)):
            centerMask = rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.5), r, width=1)
            amt = rt.binary("/", _u_center, rt.f(100.0), 1)
            if rt.binary("<", amt, rt.f(0.0)):
                color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.component_wise("mix", rt.f(1.0), centerMask, rt.unary("-", amt), width=1), 3))
            else:
                color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.construct(3, rt.f(1.0)), rt.binary("*", rt.binary("-", rt.f(1.0), centerMask, 1), amt, 1), width=3))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
