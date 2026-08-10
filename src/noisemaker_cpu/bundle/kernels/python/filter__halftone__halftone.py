def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_PATTERN = U.get("PATTERN", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_frequency = U.get("frequency", rt.f(0.0))
    _u_cyanAngle = U.get("cyanAngle", rt.f(0.0))
    _u_magentaAngle = U.get("magentaAngle", rt.f(0.0))
    _u_yellowAngle = U.get("yellowAngle", rt.f(0.0))
    _u_blackAngle = U.get("blackAngle", rt.f(0.0))
    _u_monoAngle = U.get("monoAngle", rt.f(0.0))
    _u_sharpness = U.get("sharpness", rt.f(0.0))
    _u_inkColor = U.get("inkColor", rt.construct(3, 0.0))
    _u_paperColor = U.get("paperColor", rt.construct(3, 0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.DOT_AREA_CAP = rt.f(0.5)
    g.PI = rt.f(3.141592653589793)
    g.MID_DOT_RADIUS = rt.f(0.39894228)
    g.MAX_DOT_RADIUS = rt.f(0.48)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def tonemap2__float_vec3_vec3(t, ink, paper):
        ink = rt.copy(ink, "float")
        paper = rt.copy(paper, "float")
        return rt.component_wise("mix", ink, paper, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=3)
    def rgbToCmyk__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        k = rt.binary("-", rt.f(1.0), rt.component_wise("max", rt.component_wise("max", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1), 1, "float")
        scale = rt.component_wise("max", rt.binary("-", rt.f(1.0), k, 1, "float"), rt.f(1e-05), width=1)
        cmy = rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.binary("-", rt.f(1.0), rgb, 3, "float"), rt.construct(3, k), 3, "float"), scale, 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
        return rt.construct(4, cmy, k)
    def rotate2D__vec2_float(v, angleDeg):
        v = rt.copy(v, "float")
        a = rt.component_wise("radians", angleDeg, width=1)
        co = rt.component_wise("cos", a, width=1)
        si = rt.component_wise("sin", a, width=1)
        return rt.matrix_mult(rt.construct(4, co, rt.unary("-", si), si, co), v, 2)
    def boxBlur3__vec2_vec2(uv, texel):
        uv = rt.copy(uv, "float")
        texel = rt.copy(texel, "float")
        sum = rt.construct(3, rt.f(0.0))
        y = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(1))):
                break
            x = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(1))):
                    break
                o = rt.binary("*", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), texel, 2, "float")
                sum[:] = rt.binary("+", sum, rt.swizzle(rt.texture(_u_inputTex, rt.component_wise("clamp", rt.binary("+", uv, o, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)), "rgb"), 3, "float")
        return rt.binary("/", sum, rt.f(9.0), 3, "float")
    def cellSampleFromRuv__vec2_float_vec2(ruv, angleDeg, texel):
        ruv = rt.copy(ruv, "float")
        texel = rt.copy(texel, "float")
        cellId = rt.binary("+", rt.component_wise("floor", ruv, width=2), rt.f(0.5), 2, "float")
        cellCenterGc = rotate2D__vec2_float(rt.binary("*", cellId, _u_frequency, 2, "float"), rt.unary("-", angleDeg))
        cellUV = rt.component_wise("clamp", rt.binary("/", rt.binary("-", cellCenterGc, _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
        return boxBlur3__vec2_vec2(cellUV, texel)
    def halftoneCoverage__float_float_float(d, value, sharpnessPct):
        spot = rt.binary("*", rt.component_wise("sqrt", rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1), width=1), rt.f(0.7071), 1, "float")
        softness = rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("/", sharpnessPct, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 1, "float")
        aa = rt.component_wise("max", rt.component_wise("mix", rt.binary("*", rt.fwidth(d), rt.f(1.5), 1, "float"), rt.f(0.35), softness, width=1), rt.f(1e-05), width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", spot, aa, 1, "float"), rt.binary("+", spot, aa, 1, "float"), d, width=1), 1, "float")
    def roundDotCoverage__vec2_float_float(offset, value, sharpnessPct):
        offset = rt.copy(offset, "float")
        inkAmount = rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
        centerDistance = rt.length(offset)
        inkRadius = rt.component_wise("sqrt", rt.binary("/", rt.component_wise("min", inkAmount, g.DOT_AREA_CAP, width=1), g.PI, 1, "float"), width=1)
        if rt.binary(">", inkAmount, g.DOT_AREA_CAP):
            inkRadius = rt.component_wise("mix", g.MID_DOT_RADIUS, g.MAX_DOT_RADIUS, rt.binary("/", rt.binary("-", inkAmount, g.DOT_AREA_CAP, 1, "float"), rt.binary("-", rt.f(1.0), g.DOT_AREA_CAP, 1, "float"), 1, "float"), width=1)
        softness = rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("/", sharpnessPct, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 1, "float")
        centerAA = rt.component_wise("max", rt.component_wise("mix", rt.binary("*", rt.fwidth(centerDistance), rt.f(1.5), 1, "float"), rt.f(0.35), softness, width=1), rt.f(1e-05), width=1)
        resolvedInk = rt.component_wise("smoothstep", rt.f(0.0), rt.binary("/", rt.f(1.0), rt.f(255.0), 1, "float"), value, width=1)
        return rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.unary("-", centerAA), centerAA, rt.binary("-", centerDistance, inkRadius, 1, "float"), width=1), 1, "float"), resolvedInk, 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        texel = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        alpha = rt.swizzle(rt.texture(_u_inputTex, uv), "a")
        ruvC = rt.construct(2, 0.0)
        ruvM = rt.construct(2, 0.0)
        ruvY = rt.construct(2, 0.0)
        ruvK = rt.construct(2, 0.0)
        valC = rt.f(0.0)
        valM = rt.f(0.0)
        valY = rt.f(0.0)
        valK = rt.f(0.0)
        inkC = rt.f(0.0)
        inkM = rt.f(0.0)
        inkY = rt.f(0.0)
        inkK = rt.f(0.0)
        screened = rt.construct(3, 0.0)
        value = rt.f(0.0)
        d = rt.f(0.0)
        dotOffset = rt.construct(2, 0.0)
        if rt.binary("==", _u_MODE, rt.i(0)):
            ruvC = rt.binary("/", rotate2D__vec2_float(globalCoord, _u_cyanAngle), _u_frequency, 2, "float")
            ruvM = rt.binary("/", rotate2D__vec2_float(globalCoord, _u_magentaAngle), _u_frequency, 2, "float")
            ruvY = rt.binary("/", rotate2D__vec2_float(globalCoord, _u_yellowAngle), _u_frequency, 2, "float")
            ruvK = rt.binary("/", rotate2D__vec2_float(globalCoord, _u_blackAngle), _u_frequency, 2, "float")
            valC = rt.swizzle(rgbToCmyk__vec3(cellSampleFromRuv__vec2_float_vec2(ruvC, _u_cyanAngle, texel)), "r")
            valM = rt.swizzle(rgbToCmyk__vec3(cellSampleFromRuv__vec2_float_vec2(ruvM, _u_magentaAngle, texel)), "g")
            valY = rt.swizzle(rgbToCmyk__vec3(cellSampleFromRuv__vec2_float_vec2(ruvY, _u_yellowAngle, texel)), "b")
            valK = rt.swizzle(rgbToCmyk__vec3(cellSampleFromRuv__vec2_float_vec2(ruvK, _u_blackAngle, texel)), "a")
            inkC = roundDotCoverage__vec2_float_float(rt.binary("-", rt.component_wise("fract", ruvC, width=2), rt.f(0.5), 2, "float"), valC, _u_sharpness)
            inkM = roundDotCoverage__vec2_float_float(rt.binary("-", rt.component_wise("fract", ruvM, width=2), rt.f(0.5), 2, "float"), valM, _u_sharpness)
            inkY = roundDotCoverage__vec2_float_float(rt.binary("-", rt.component_wise("fract", ruvY, width=2), rt.f(0.5), 2, "float"), valY, _u_sharpness)
            inkK = roundDotCoverage__vec2_float_float(rt.binary("-", rt.component_wise("fract", ruvK, width=2), rt.f(0.5), 2, "float"), valK, _u_sharpness)
            screened = rt.binary("*", rt.binary("-", rt.construct(3, rt.f(1.0)), rt.construct(3, inkC, inkM, inkY), 3, "float"), rt.binary("-", rt.f(1.0), inkK, 1, "float"), 3, "float")
            g.fragColor[:] = rt.construct(4, screened, alpha)
            return
        else:
            value = rt.f(0.0)
            d = rt.f(0.0)
            dotOffset = rt.construct(2, rt.f(0.0))
            center = rt.construct(2, 0.0)
            rd = rt.f(0.0)
            ruv = rt.construct(2, 0.0)
            off = rt.construct(2, 0.0)
            if rt.binary("==", _u_PATTERN, rt.i(2)):
                center = rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float")
                value = rt.binary("-", rt.f(1.0), lum__vec3(boxBlur3__vec2_vec2(uv, texel)), 1, "float")
                rd = rt.binary("/", rt.length(rt.binary("-", globalCoord, center, 2, "float")), _u_frequency, 1, "float")
                d = rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", rd, width=1), rt.f(0.5), 1, "float"), width=1)
            else:
                ruv = rt.binary("/", rotate2D__vec2_float(globalCoord, _u_monoAngle), _u_frequency, 2, "float")
                value = rt.binary("-", rt.f(1.0), lum__vec3(cellSampleFromRuv__vec2_float_vec2(ruv, _u_monoAngle, texel)), 1, "float")
                off = rt.binary("-", rt.component_wise("fract", ruv, width=2), rt.f(0.5), 2, "float")
                dotOffset[:] = off
                if rt.binary("==", _u_PATTERN, rt.i(1)):
                    d = rt.component_wise("abs", rt.swizzle(off, "y"), width=1)
                else:
                    d = rt.length(off)
            ink = rt.f(0.0)
            if rt.binary("==", _u_PATTERN, rt.i(0)):
                ink = roundDotCoverage__vec2_float_float(dotOffset, value, _u_sharpness)
            else:
                ink = halftoneCoverage__float_float_float(d, value, _u_sharpness)
            g.fragColor[:] = rt.construct(4, tonemap2__float_vec3_vec3(rt.binary("-", rt.f(1.0), ink, 1, "float"), _u_inkColor, _u_paperColor), alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
run_pixel.uses_derivatives = True
