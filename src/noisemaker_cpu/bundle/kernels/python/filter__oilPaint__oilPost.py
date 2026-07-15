def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U["MODE"]
    _u_inputTex = T["inputTex"]
    _u_flatTex = T["flatTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_size = U["size"]
    _u_detail = U["detail"]
    _u_textureAmount = U["textureAmount"]
    _u_seed = U["seed"]
    def hash12__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3)), 3)
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1), rt.swizzle(p3, "z"), 1), width=1)
    def vnoise__vec2(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2), 2), 2)
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2)), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2)), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2)), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def fbm__vec2(p):
        p = rt.copy(p)
        v = rt.f(0.0)
        a = rt.f(0.5)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(5))):
                break
            v = rt.binary("+", v, rt.binary("*", a, vnoise__vec2(p), 1), 1)
            p = rt.binary("*", p, rt.f(2.03), 2)
            a = rt.binary("*", a, rt.f(0.5), 1)
        return v
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradientFlat__vec2(uv):
        uv = rt.copy(uv)
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2)
        tl = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2), 2)), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2), 2)), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2), 2)), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2), 2)), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2), 2)), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1), 1), br, 1), tl, 1), rt.binary("*", rt.f(2.0), l, 1), 1), bl, 1), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1), 1), tr, 1), bl, 1), rt.binary("*", rt.f(2.0), b, 1), 1), br, 1))
    def tent3x3__vec2(uv):
        uv = rt.copy(uv)
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2)
        sum = rt.construct(3, rt.f(0.0))
        wsum = rt.f(0.0)
        dy = rt.unary("-", rt.i(1))
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                dy = rt.binary("+", dy, rt.i(1), 1)
            _for1_first = False
            if not (rt.binary("<=", dy, rt.i(1))):
                break
            dx = rt.unary("-", rt.i(1))
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    dx = rt.binary("+", dx, rt.i(1), 1)
                _for2_first = False
                if not (rt.binary("<=", dx, rt.i(1))):
                    break
                w = rt.binary("*", (rt.f(2.0) if rt.binary("==", dx, rt.i(0)) else rt.f(1.0)), (rt.f(2.0) if rt.binary("==", dy, rt.i(0)) else rt.f(1.0)), 1)
                sum = rt.binary("+", sum, rt.binary("*", rt.swizzle(rt.texture(_u_flatTex, rt.binary("+", uv, rt.binary("*", rt.construct(2, dx, dy), px, 2), 2)), "rgb"), w, 3), 3)
                wsum = rt.binary("+", wsum, w, 1)
        return rt.binary("/", sum, wsum, 3)
    def sCurve__float(x):
        t = rt.component_wise("clamp", x, rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("*", rt.binary("*", t, t, 1), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), t, 1), 1), 1)
    def modeColor__vec2_vec3_vec2(uv, c, globalCoord):
        uv = rt.copy(uv)
        c = rt.copy(c)
        globalCoord = rt.copy(globalCoord)
        if rt.binary("==", _u_MODE, rt.i(0)):
            return c
        else:
            if rt.binary("==", _u_MODE, rt.i(1)):
                blurred = tent3x3__vec2(uv)
                return rt.binary("+", c, rt.binary("*", rt.binary("-", c, blurred, 3), rt.binary("/", _u_detail, rt.f(25.0), 1), 3), 3)
            else:
                if rt.binary("==", _u_MODE, rt.i(2)):
                    levels = rt.component_wise("floor", rt.binary("+", rt.component_wise("mix", rt.f(8.0), rt.f(3.0), rt.binary("/", _u_detail, rt.f(100.0), 1), width=1), rt.f(0.5), 1), width=1)
                    poster = rt.binary("/", rt.component_wise("floor", rt.binary("*", c, levels, 3), width=3), levels, 3)
                    gradMag = rt.length(lumGradientFlat__vec2(uv))
                    edgeDarken = rt.binary("*", rt.component_wise("clamp", rt.binary("*", gradMag, rt.f(1.5), 1), rt.f(0.0), rt.f(1.0), width=1), rt.f(0.15), 1)
                    return rt.binary("*", poster, rt.binary("-", rt.f(1.0), edgeDarken, 1), 3)
                else:
                    if rt.binary("==", _u_MODE, rt.i(3)):
                        gradMag = rt.length(lumGradientFlat__vec2(uv))
                        darkened = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(0.6), rt.binary("/", _u_detail, rt.f(100.0), 1), 1), gradMag, 1), 1), 3)
                        return rt.construct(3, sCurve__float(rt.swizzle(darkened, "r")), sCurve__float(rt.swizzle(darkened, "g")), sCurve__float(rt.swizzle(darkened, "b")))
                    else:
                        if rt.binary("==", _u_MODE, rt.i(4)):
                            blurred = tent3x3__vec2(uv)
                            return rt.component_wise("mix", c, blurred, rt.binary("/", _u_detail, rt.f(100.0), 1), width=3)
                        else:
                            band = fbm__vec2(rt.binary("/", rt.binary("+", globalCoord, rt.binary("*", _u_seed, rt.f(37.0), 1), 2), rt.binary("+", rt.f(4.0), _u_size, 1), 2))
                            shift = rt.binary("*", rt.binary("*", rt.binary("-", rt.binary("*", band, rt.f(2.0), 1), rt.f(1.0), 1), rt.binary("/", _u_detail, rt.f(100.0), 1), 1), rt.f(0.25), 1)
                            return rt.component_wise("clamp", rt.binary("+", c, rt.construct(3, shift), 3), rt.f(0.0), rt.f(1.0), width=3)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        src = rt.texture(_u_inputTex, uv)
        c = rt.swizzle(rt.texture(_u_flatTex, uv), "rgb")
        globalCoord = rt.binary("+", rt.component_wise("floor", rt.swizzle(ctx.frag_coord, "xy"), width=2), _u_tileOffset, 2)
        outc = modeColor__vec2_vec3_vec2(uv, c, globalCoord)
        grained = rt.binary("*", outc, rt.binary("+", rt.f(0.85), rt.binary("*", rt.f(0.3), vnoise__vec2(rt.binary("/", globalCoord, rt.f(2.0), 2)), 1), 1), 3)
        outc = rt.component_wise("mix", outc, grained, rt.binary("*", rt.binary("/", _u_textureAmount, rt.f(100.0), 1), rt.f(0.5), 1), width=3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", outc, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
