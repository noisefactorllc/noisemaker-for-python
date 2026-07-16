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
    _u_polarMode = U["polarMode"]
    _u_speed = U["speed"]
    _u_rotation = U["rotation"]
    _u_scale = U["scale"]
    _u_aspectLens = U["aspectLens"]
    _u_antialias = U["antialias"]
    g.TAU = rt.f(6.28318530718)
    def smod__float_float(v, m):
        return rt.binary("*", m, rt.binary("-", rt.binary("-", rt.f(0.75), rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", v, width=1), rt.f(0.5), 1, "float"), width=1), 1, "float"), rt.f(0.25), 1, "float"), 1, "float")
    def smod2__vec2_float(v, m):
        v = rt.copy(v)
        return rt.binary("*", m, rt.binary("-", rt.binary("-", rt.f(0.75), rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", v, width=2), rt.f(0.5), 2, "float"), width=2), 2, "float"), rt.f(0.25), 2, "float"), 2, "float")
    def polarCoords__vec2_float(uv, aspect):
        uv = rt.copy(uv)
        uv = rt.binary("-", uv, rt.f(0.5), 2, "float")
        if _u_aspectLens:
            uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), aspect, 1, "float"))
        coord = rt.construct(2, rt.binary("+", rt.binary("/", rt.component_wise("atan", rt.swizzle(uv, "y"), rt.swizzle(uv, "x"), width=1), g.TAU, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.length(uv), rt.binary("*", _u_scale, rt.f(0.075), 1, "float"), 1, "float"))
        coord = rt.assign_swizzle(coord, "x", smod__float_float(rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", _u_time, rt.unary("-", _u_rotation), 1, "float"), 1, "float"), rt.f(1.0)))
        coord = rt.assign_swizzle(coord, "y", smod__float_float(rt.binary("+", rt.swizzle(coord, "y"), rt.binary("*", _u_time, _u_speed, 1, "float"), 1, "float"), rt.f(1.0)))
        return coord
    def vortexCoords__vec2_float(uv, aspect):
        uv = rt.copy(uv)
        uv = rt.binary("-", uv, rt.f(0.5), 2, "float")
        if _u_aspectLens:
            uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), aspect, 1, "float"))
        r2 = rt.binary("-", rt.dot(uv, uv), rt.binary("*", _u_scale, rt.f(0.01), 1, "float"), 1, "float")
        uv = rt.binary("/", uv, r2, 2, "float")
        uv = rt.assign_swizzle(uv, "x", smod__float_float(rt.binary("+", rt.swizzle(uv, "x"), rt.binary("*", _u_time, rt.unary("-", _u_rotation), 1, "float"), 1, "float"), rt.f(1.0)))
        uv = rt.assign_swizzle(uv, "y", smod__float_float(rt.binary("+", rt.swizzle(uv, "y"), rt.binary("*", _u_time, _u_speed, 1, "float"), 1, "float"), rt.f(1.0)))
        return uv
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
        coord = rt.construct(2, 0.0)
        if rt.binary("==", _u_polarMode, rt.i(0)):
            coord = polarCoords__vec2_float(uv, aspect)
        else:
            coord = vortexCoords__vec2_float(uv, aspect)
        if _u_antialias:
            dx = rt.dFdx(coord)
            dy = rt.dFdy(coord)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", coord, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", coord, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", coord, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", coord, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            g.fragColor = rt.texture(_u_inputTex, coord)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.uses_derivatives = True
