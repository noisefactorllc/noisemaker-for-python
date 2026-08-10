def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_sobelMetric = U.get("sobelMetric", rt.f(0.0))
    _u_width = U.get("width", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def luminance__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        return rt.dot(rgb, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def distance_metric__float_float_int(gx, gy, metric):
        abs_gx = rt.component_wise("abs", gx, width=1)
        abs_gy = rt.component_wise("abs", gy, width=1)
        cross = rt.f(0.0)
        if rt.binary("==", metric, rt.i(1)):
            return rt.binary("+", abs_gx, abs_gy, 1, "float")
        else:
            if rt.binary("==", metric, rt.i(2)):
                return rt.component_wise("max", abs_gx, abs_gy, width=1)
            else:
                if rt.binary("==", metric, rt.i(3)):
                    cross = rt.binary("/", rt.binary("+", abs_gx, abs_gy, 1, "float"), rt.f(1.414), 1, "float")
                    return rt.component_wise("max", cross, rt.component_wise("max", abs_gx, abs_gy, width=1), width=1)
        return rt.component_wise("sqrt", rt.binary("+", rt.binary("*", gx, gx, 1, "float"), rt.binary("*", gy, gy, 1, "float"), 1, "float"), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        texel = rt.binary("/", _u_width, _u_resolution, 2, "float")
        base = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        tl = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.swizzle(texel, "x")), rt.unary("-", rt.swizzle(texel, "y"))), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        tc = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(texel, "y"))), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        tr = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.unary("-", rt.swizzle(texel, "y"))), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        ml = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.swizzle(texel, "x")), rt.f(0.0)), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        mr = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        bl = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.swizzle(texel, "x")), rt.swizzle(texel, "y")), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        bc = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        br = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.swizzle(texel, "y")), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb"))
        gx = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("-", rt.unary("-", tl), rt.binary("*", rt.f(2.0), ml, 1, "float"), 1, "float"), bl, 1, "float"), tr, 1, "float"), rt.binary("*", rt.f(2.0), mr, 1, "float"), 1, "float"), br, 1, "float")
        gy = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("-", rt.unary("-", tl), rt.binary("*", rt.f(2.0), tc, 1, "float"), 1, "float"), tr, 1, "float"), bl, 1, "float"), rt.binary("*", rt.f(2.0), bc, 1, "float"), 1, "float"), br, 1, "float")
        metric = rt.construct(1, _u_sobelMetric, base="int")
        edge = rt.component_wise("clamp", rt.binary("*", distance_metric__float_float_int(gx, gy, metric), rt.f(3.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        glow = rt.binary("*", rt.binary("*", edge, rt.swizzle(base, "rgb"), 3, "float"), rt.f(2.0), 3, "float")
        result = rt.binary("-", rt.construct(3, rt.f(1.0)), rt.binary("*", rt.binary("-", rt.construct(3, rt.f(1.0)), rt.swizzle(base, "rgb"), 3, "float"), rt.binary("-", rt.construct(3, rt.f(1.0)), glow, 3, "float"), 3, "float"), 3, "float")
        mixed = rt.component_wise("mix", rt.swizzle(base, "rgb"), result, _u_alpha, width=3)
        g.fragColor[:] = rt.construct(4, rt.component_wise("clamp", mixed, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
