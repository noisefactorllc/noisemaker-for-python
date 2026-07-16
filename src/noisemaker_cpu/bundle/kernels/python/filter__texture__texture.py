def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_time = U.get("time", rt.f(0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    _u_contrast = U.get("contrast", rt.f(0.0))
    _u_mono = U.get("mono", False)
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.PI = rt.f(3.14159265359)
    g.INV_UINT32_MAX = rt.binary("/", rt.f(1.0), rt.f(4294967295.0), 1, "float")
    g.Z_LOOP = rt.i(2)
    g.SHADE_GAIN = rt.f(4.4)
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def s_curve01__float(value):
        c = clamp01__float(value)
        return rt.binary("*", rt.binary("*", c, c, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), c, 1, "float"), 1, "float"), 1, "float")
    def fade__float(t):
        return rt.binary("*", rt.binary("*", t, t, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), 1, "float")
    def freq_for_shape__float_vec2(base_freq, dims):
        dims = rt.copy(dims, "float")
        w = rt.component_wise("max", rt.swizzle(dims, "x"), rt.f(1.0), width=1)
        h = rt.component_wise("max", rt.swizzle(dims, "y"), rt.f(1.0), width=1)
        if rt.binary("<", rt.component_wise("abs", rt.binary("-", w, h, 1, "float"), width=1), rt.f(0.5)):
            return rt.construct(2, base_freq, base_freq)
        if rt.binary(">", w, h):
            return rt.construct(2, base_freq, rt.binary("/", rt.binary("*", base_freq, w, 1, "float"), h, 1, "float"))
        return rt.construct(2, rt.binary("/", rt.binary("*", base_freq, h, 1, "float"), w, 1, "float"), base_freq)
    def hash_uint__uint(x):
        x = rt.binary("^", x, rt.binary(">>", x, rt.i(16), 1, "uint"), 1, "uint")
        x = rt.binary("*", x, rt.i(2146121005), 1, "uint")
        x = rt.binary("^", x, rt.binary(">>", x, rt.i(15), 1, "uint"), 1, "uint")
        x = rt.binary("*", x, rt.i(2221713035), 1, "uint")
        x = rt.binary("^", x, rt.binary(">>", x, rt.i(16), 1, "uint"), 1, "uint")
        return x
    def fast_hash__ivec3_uint(p, salt):
        p = rt.copy(p, "int")
        h = rt.binary("^", salt, rt.i(2654435769), 1, "uint")
        h = rt.binary("^", h, rt.binary("*", rt.construct(1, rt.swizzle(p, "x"), base="uint"), rt.i(668265261), 1, "uint"), 1, "uint")
        h = rt.hash_uint(h)
        h = rt.binary("^", h, rt.binary("*", rt.construct(1, rt.swizzle(p, "y"), base="uint"), rt.i(3266489909), 1, "uint"), 1, "uint")
        h = rt.hash_uint(h)
        h = rt.binary("^", h, rt.binary("*", rt.construct(1, rt.swizzle(p, "z"), base="uint"), rt.i(374761393), 1, "uint"), 1, "uint")
        h = rt.hash_uint(h)
        return rt.binary("*", rt.construct(1, h), g.INV_UINT32_MAX, 1, "float")
    def value_noise__vec2_vec2_float_uint(uv, freq, motion, salt):
        uv = rt.copy(uv, "float")
        freq = rt.copy(freq, "float")
        scaled_uv = rt.binary("*", uv, rt.component_wise("max", freq, rt.construct(2, rt.f(1.0), rt.f(1.0)), width=2), 2, "float")
        cell_floor = rt.component_wise("floor", scaled_uv, width=2)
        frac_part = rt.component_wise("fract", scaled_uv, width=2)
        base_cell = rt.construct(2, cell_floor, base="int")
        z_floor = rt.component_wise("floor", motion, width=1)
        z_frac = rt.component_wise("fract", motion, width=1)
        z0 = rt.binary("%", rt.construct(1, z_floor, base="int"), g.Z_LOOP, 1, "int")
        z1 = rt.binary("%", rt.binary("+", z0, rt.i(1), 1, "int"), g.Z_LOOP, 1, "int")
        c000 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(0), 1, "int"), z0, base="int"), salt)
        c100 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(0), 1, "int"), z0, base="int"), salt)
        c010 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(1), 1, "int"), z0, base="int"), salt)
        c110 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(1), 1, "int"), z0, base="int"), salt)
        c001 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(0), 1, "int"), z1, base="int"), salt)
        c101 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(0), 1, "int"), z1, base="int"), salt)
        c011 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(1), 1, "int"), z1, base="int"), salt)
        c111 = fast_hash__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(base_cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(base_cell, "y"), rt.i(1), 1, "int"), z1, base="int"), salt)
        tx = fade__float(rt.swizzle(frac_part, "x"))
        ty = fade__float(rt.swizzle(frac_part, "y"))
        tz = fade__float(z_frac)
        x00 = rt.component_wise("mix", c000, c100, tx, width=1)
        x10 = rt.component_wise("mix", c010, c110, tx, width=1)
        x01 = rt.component_wise("mix", c001, c101, tx, width=1)
        x11 = rt.component_wise("mix", c011, c111, tx, width=1)
        y0 = rt.component_wise("mix", x00, x10, ty, width=1)
        y1 = rt.component_wise("mix", x01, x11, ty, width=1)
        return rt.component_wise("mix", y0, y1, tz, width=1)
    def height_paper__vec2_vec2_float(uv, base_freq, motion):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        freq = rt.component_wise("max", base_freq, rt.construct(2, rt.f(1.0), rt.f(1.0)), width=2)
        amplitude = rt.f(0.5)
        accum = rt.f(0.0)
        total = rt.f(0.0)
        octave = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                octave = rt.binary("+", octave, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", octave, rt.i(3))):
                break
            salt = rt.binary("*", rt.i(2654435769), rt.construct(1, rt.binary("+", octave, rt.i(1), 1, "int"), base="uint"), 1, "uint")
            samp = value_noise__vec2_vec2_float_uint(uv, freq, rt.binary("+", motion, rt.binary("*", rt.construct(1, octave), rt.f(0.37), 1, "float"), 1, "float"), salt)
            ridged = rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", samp, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float")
            accum = rt.binary("+", accum, rt.binary("*", ridged, amplitude, 1, "float"), 1, "float")
            total = rt.binary("+", total, amplitude, 1, "float")
            freq = rt.binary("*", freq, rt.f(2.0), 2, "float")
            amplitude = rt.binary("*", amplitude, rt.f(0.55), 1, "float")
        return (clamp01__float(rt.binary("/", accum, total, 1, "float")) if rt.binary(">", total, rt.f(0.0)) else clamp01__float(accum))
    def height_stucco__vec2_vec2_float(uv, base_freq, motion):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        freq = rt.component_wise("max", base_freq, rt.construct(2, rt.f(1.0), rt.f(1.0)), width=2)
        amplitude = rt.f(0.5)
        accum = rt.f(0.0)
        total = rt.f(0.0)
        octave = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                octave = rt.binary("+", octave, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", octave, rt.i(2))):
                break
            salt = rt.binary("*", rt.i(2654435769), rt.construct(1, rt.binary("+", octave, rt.i(1), 1, "int"), base="uint"), 1, "uint")
            samp = value_noise__vec2_vec2_float_uint(uv, freq, rt.binary("+", motion, rt.binary("*", rt.construct(1, octave), rt.f(0.37), 1, "float"), 1, "float"), salt)
            accum = rt.binary("+", accum, rt.binary("*", samp, amplitude, 1, "float"), 1, "float")
            total = rt.binary("+", total, amplitude, 1, "float")
            freq = rt.binary("*", freq, rt.f(2.0), 2, "float")
            amplitude = rt.binary("*", amplitude, rt.f(0.5), 1, "float")
        return (clamp01__float(rt.binary("/", accum, total, 1, "float")) if rt.binary(">", total, rt.f(0.0)) else clamp01__float(accum))
    def height_canvas__vec2_vec2_float(uv, base_freq, motion):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        st = rt.binary("*", uv, base_freq, 2, "float")
        warpX = rt.component_wise("abs", rt.component_wise("sin", rt.binary("*", rt.swizzle(st, "x"), g.PI, 1, "float"), width=1), width=1)
        weftY = rt.component_wise("abs", rt.component_wise("sin", rt.binary("*", rt.swizzle(st, "y"), g.PI, 1, "float"), width=1), width=1)
        weave = rt.binary("*", warpX, weftY, 1, "float")
        noise = value_noise__vec2_vec2_float_uint(uv, rt.binary("*", base_freq, rt.f(0.5), 2, "float"), motion, rt.i(305419896))
        return clamp01__float(rt.binary("+", rt.binary("*", weave, rt.f(0.85), 1, "float"), rt.binary("*", noise, rt.f(0.15), 1, "float"), 1, "float"))
    def height_halftone__vec2_vec2(uv, base_freq):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        st = rt.binary("*", uv, base_freq, 2, "float")
        cell = rt.binary("-", rt.component_wise("fract", st, width=2), rt.f(0.5), 2, "float")
        dot = rt.binary("-", rt.f(1.0), clamp01__float(rt.binary("*", rt.length(cell), rt.f(3.0), 1, "float")), 1, "float")
        return rt.binary("*", dot, dot, 1, "float")
    def height_crosshatch__vec2_vec2(uv, base_freq):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        st = rt.binary("*", uv, base_freq, 2, "float")
        d1 = rt.component_wise("abs", rt.component_wise("sin", rt.binary("*", rt.binary("+", rt.swizzle(st, "x"), rt.swizzle(st, "y"), 1, "float"), g.PI, 1, "float"), width=1), width=1)
        d2 = rt.component_wise("abs", rt.component_wise("sin", rt.binary("*", rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(st, "y"), 1, "float"), g.PI, 1, "float"), width=1), width=1)
        return clamp01__float(rt.binary("*", d1, d2, 1, "float"))
    def height_field__vec2_vec2_float(uv, base_freq, motion):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        if rt.binary("==", _u_MODE, rt.i(0)):
            return height_canvas__vec2_vec2_float(uv, base_freq, motion)
        else:
            if rt.binary("==", _u_MODE, rt.i(1)):
                return height_crosshatch__vec2_vec2(uv, base_freq)
            else:
                if rt.binary("==", _u_MODE, rt.i(2)):
                    return height_halftone__vec2_vec2(uv, base_freq)
                else:
                    if rt.binary("==", _u_MODE, rt.i(4)):
                        return height_stucco__vec2_vec2_float(uv, base_freq, motion)
                    else:
                        return height_paper__vec2_vec2_float(uv, base_freq, motion)
    def material_hash__ivec2_uint_uint(p, salt, layer):
        p = rt.copy(p, "int")
        h = rt.binary("^", salt, rt.binary("*", layer, rt.i(2654435769), 1, "uint"), 1, "uint")
        h = rt.binary("^", h, rt.binary("*", rt.construct(1, rt.swizzle(p, "x"), base="uint"), rt.i(668265261), 1, "uint"), 1, "uint")
        h = rt.hash_uint(h)
        h = rt.binary("^", h, rt.binary("*", rt.construct(1, rt.swizzle(p, "y"), base="uint"), rt.i(3266489909), 1, "uint"), 1, "uint")
        return rt.hash_uint(h)
    def material_gradient__ivec2_uint_uint(p, salt, layer):
        p = rt.copy(p, "int")
        h = material_hash__ivec2_uint_uint(p, salt, layer)
        gradient = rt.binary("-", rt.binary("*", rt.construct(2, rt.construct(1, rt.binary("&", h, rt.i(65535), 1, "uint")), rt.construct(1, rt.binary(">>", h, rt.i(16), 1, "uint"))), rt.binary("/", rt.f(2.0), rt.f(65535.0), 1, "float"), 2, "float"), rt.f(1.0), 2, "float")
        return rt.binary("*", gradient, rt.component_wise("inversesqrt", rt.component_wise("max", rt.dot(gradient, gradient), rt.f(1e-06), width=1), width=1), 2, "float")
    def material_fade__vec2(t):
        t = rt.copy(t, "float")
        return rt.binary("*", rt.binary("*", rt.binary("*", t, t, 2, "float"), t, 2, "float"), rt.binary("+", rt.binary("*", t, rt.binary("-", rt.binary("*", t, rt.f(6.0), 2, "float"), rt.f(15.0), 2, "float"), 2, "float"), rt.f(10.0), 2, "float"), 2, "float")
    def material_gradient_layer__vec2_uint_uint(p, salt, layer):
        p = rt.copy(p, "float")
        cell = rt.construct(2, rt.component_wise("floor", p, width=2), base="int")
        local = rt.component_wise("fract", p, width=2)
        n00 = rt.dot(material_gradient__ivec2_uint_uint(cell, salt, layer), local)
        n10 = rt.dot(material_gradient__ivec2_uint_uint(rt.binary("+", cell, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), salt, layer), rt.binary("-", local, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"))
        n01 = rt.dot(material_gradient__ivec2_uint_uint(rt.binary("+", cell, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), salt, layer), rt.binary("-", local, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"))
        n11 = rt.dot(material_gradient__ivec2_uint_uint(rt.binary("+", cell, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), salt, layer), rt.binary("-", local, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"))
        blend = material_fade__vec2(local)
        return rt.component_wise("mix", rt.component_wise("mix", n00, n10, rt.swizzle(blend, "x"), width=1), rt.component_wise("mix", n01, n11, rt.swizzle(blend, "x"), width=1), rt.swizzle(blend, "y"), width=1)
    def material_noise__vec2_vec2_float_uint(globalPixel, cellSize, motion, salt):
        globalPixel = rt.copy(globalPixel, "float")
        cellSize = rt.copy(cellSize, "float")
        p = rt.binary("/", globalPixel, rt.component_wise("max", cellSize, rt.construct(2, rt.f(0.5)), width=2), 2, "float")
        zFloor = rt.component_wise("floor", motion, width=1)
        z0 = rt.binary("%", rt.construct(1, zFloor, base="int"), g.Z_LOOP, 1, "int")
        z1 = rt.binary("%", rt.binary("+", z0, rt.i(1), 1, "int"), g.Z_LOOP, 1, "int")
        n0 = material_gradient_layer__vec2_uint_uint(p, salt, rt.construct(1, z0, base="uint"))
        n1 = material_gradient_layer__vec2_uint_uint(p, salt, rt.construct(1, z1, base="uint"))
        n = rt.component_wise("mix", n0, n1, rt.swizzle(material_fade__vec2(rt.construct(2, rt.component_wise("fract", motion, width=1))), "x"), width=1)
        return clamp01__float(rt.binary("+", rt.f(0.5), rt.binary("*", n, rt.f(0.72), 1, "float"), 1, "float"))
    def material_soft__vec2_float_uint_float(globalPixel, motion, salt, size):
        globalPixel = rt.copy(globalPixel, "float")
        primaryCell = rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(3.25), 1, "float"), rt.f(1.5), width=1))
        primary = material_noise__vec2_vec2_float_uint(globalPixel, primaryCell, motion, salt)
        secondary = material_noise__vec2_vec2_float_uint(rt.binary("+", globalPixel, rt.construct(2, rt.f(17.31), rt.f(29.17)), 2, "float"), rt.binary("*", primaryCell, rt.f(1.87), 2, "float"), rt.binary("+", motion, rt.f(0.41), 1, "float"), rt.binary("^", salt, rt.i(1757159915), 1, "uint"))
        return rt.binary("+", rt.binary("*", primary, rt.f(0.68), 1, "float"), rt.binary("*", secondary, rt.f(0.32), 1, "float"), 1, "float")
    def material_directional__vec2_float_uint_float(globalPixel, motion, salt, size):
        globalPixel = rt.copy(globalPixel, "float")
        primaryCell = rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(22.0), 1, "float"), rt.f(8.0), width=1), rt.component_wise("max", rt.binary("*", size, rt.f(2.0), 1, "float"), rt.f(1.25), width=1))
        secondaryCell = rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(37.0), 1, "float"), rt.f(13.0), width=1), rt.component_wise("max", rt.binary("*", size, rt.f(3.7), 1, "float"), rt.f(2.3), width=1))
        primary = material_noise__vec2_vec2_float_uint(globalPixel, primaryCell, motion, salt)
        secondary = material_noise__vec2_vec2_float_uint(rt.binary("+", globalPixel, rt.construct(2, rt.f(19.37), rt.f(11.83)), 2, "float"), secondaryCell, rt.binary("+", motion, rt.f(0.41), 1, "float"), rt.binary("^", salt, rt.i(1757159915), 1, "uint"))
        return rt.binary("+", rt.binary("*", primary, rt.f(0.72), 1, "float"), rt.binary("*", secondary, rt.f(0.28), 1, "float"), 1, "float")
    def material_sprinkles__vec2_float_uint_float(globalPixel, motion, salt, size):
        globalPixel = rt.copy(globalPixel, "float")
        p = rt.binary("+", rt.binary("/", globalPixel, rt.component_wise("max", rt.binary("*", rt.f(4.0), size, 1, "float"), rt.f(1.0), width=1), 2, "float"), rt.construct(2, rt.binary("*", motion, rt.f(0.31), 1, "float"), rt.binary("*", motion, rt.f(0.19), 1, "float")), 2, "float")
        baseCell = rt.construct(2, rt.component_wise("floor", p, width=2), base="int")
        local = rt.component_wise("fract", p, width=2)
        nearest = rt.f(10.0)
        y = rt.unary("-", rt.i(1))
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<=", y, rt.i(1))):
                break
            x = rt.unary("-", rt.i(1))
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for3_first = False
                if not (rt.binary("<=", x, rt.i(1))):
                    break
                cell = rt.binary("+", baseCell, rt.construct(2, x, y, base="int"), 2, "int")
                jx = rt.binary("-", fast_hash__ivec3_uint(rt.construct(3, cell, rt.i(0), base="int"), salt), rt.f(0.5), 1, "float")
                jy = rt.binary("-", fast_hash__ivec3_uint(rt.construct(3, cell, rt.i(1), base="int"), rt.binary("^", salt, rt.i(1757159915), 1, "uint")), rt.f(0.5), 1, "float")
                point = rt.binary("+", rt.binary("+", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), rt.f(0.5), 2, "float"), rt.binary("*", rt.construct(2, jx, jy), rt.f(0.6), 2, "float"), 2, "float")
                nearest = rt.component_wise("min", nearest, rt.length(rt.binary("-", local, point, 2, "float")), width=1)
        return rt.component_wise("mix", rt.f(0.45), rt.f(1.0), rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.1), rt.f(0.22), nearest, width=1), 1, "float"), width=1)
    def material_edge_mask__vec2_vec2(uv, pixelStep):
        uv = rt.copy(uv, "float")
        pixelStep = rt.copy(pixelStep, "float")
        l = rt.dot(rt.swizzle(rt.texture(_u_inputTex, rt.binary("-", uv, rt.construct(2, rt.swizzle(pixelStep, "x"), rt.f(0.0)), 2, "float")), "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        r = rt.dot(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(pixelStep, "x"), rt.f(0.0)), 2, "float")), "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        d = rt.dot(rt.swizzle(rt.texture(_u_inputTex, rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(pixelStep, "y")), 2, "float")), "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        u = rt.dot(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(pixelStep, "y")), 2, "float")), "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        return rt.component_wise("clamp", rt.binary("*", rt.length(rt.construct(2, rt.binary("-", r, l, 1, "float"), rt.binary("-", u, d, 1, "float"))), rt.f(6.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
    def material_value__vec2_vec2_vec2_float_uint(globalPixel, dims, uv, motion, salt):
        globalPixel = rt.copy(globalPixel, "float")
        dims = rt.copy(dims, "float")
        uv = rt.copy(uv, "float")
        size = rt.component_wise("max", _u_scale, rt.f(0.1), width=1)
        if rt.binary("==", _u_MODE, rt.i(6)):
            return material_soft__vec2_float_uint_float(globalPixel, motion, salt, size)
        else:
            if rt.binary("==", _u_MODE, rt.i(7)):
                return material_sprinkles__vec2_float_uint_float(globalPixel, motion, salt, size)
            else:
                if rt.binary("==", _u_MODE, rt.i(8)):
                    a = material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.binary("*", rt.f(13.0), size, 1, "float")), motion, salt)
                    b = material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.binary("*", rt.f(6.0), size, 1, "float")), rt.binary("+", motion, rt.f(0.31), 1, "float"), rt.binary("^", salt, rt.i(2654435769), 1, "uint"))
                    c = material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.binary("*", rt.f(2.5), size, 1, "float")), rt.binary("+", motion, rt.f(0.67), 1, "float"), rt.binary("^", salt, rt.i(2246822507), 1, "uint"))
                    return rt.binary("+", rt.binary("+", rt.binary("*", a, rt.f(0.58), 1, "float"), rt.binary("*", b, rt.f(0.28), 1, "float"), 1, "float"), rt.binary("*", c, rt.f(0.14), 1, "float"), 1, "float")
                else:
                    if rt.binary("==", _u_MODE, rt.i(9)):
                        n = material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(1.5), 1, "float"), rt.f(0.8), width=1)), motion, salt)
                        return s_curve01__float(s_curve01__float(n))
                    else:
                        if rt.binary("==", _u_MODE, rt.i(10)):
                            return material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.binary("*", rt.f(4.5), size, 1, "float")), motion, salt)
                        else:
                            if rt.binary("==", _u_MODE, rt.i(11)):
                                return rt.component_wise("step", rt.f(0.5), material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(1.5), 1, "float"), rt.f(0.8), width=1)), motion, salt), width=1)
                            else:
                                if rt.binary("==", _u_MODE, rt.i(12)):
                                    return material_directional__vec2_float_uint_float(globalPixel, motion, salt, size)
                                else:
                                    if rt.binary("==", _u_MODE, rt.i(13)):
                                        return material_directional__vec2_float_uint_float(rt.swizzle(globalPixel, "yx"), motion, salt, size)
                                    else:
                                        if rt.binary("==", _u_MODE, rt.i(14)):
                                            n = material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(1.5), 1, "float"), rt.f(0.8), width=1)), motion, salt)
                                            return rt.component_wise("mix", rt.f(0.5), n, material_edge_mask__vec2_vec2(uv, rt.binary("/", rt.f(1.0), dims, 2, "float")), width=1)
                                        else:
                                            return material_noise__vec2_vec2_float_uint(globalPixel, rt.construct(2, rt.component_wise("max", rt.binary("*", size, rt.f(1.5), 1, "float"), rt.f(0.8), width=1)), motion, salt)
    def shape_material__float(raw):
        amount = rt.binary("/", _u_intensity, rt.f(40.0), 1, "float")
        shaped = rt.binary("+", rt.binary("*", raw, amount, 1, "float"), rt.binary("*", rt.f(0.5), rt.binary("-", rt.f(1.0), amount, 1, "float"), 1, "float"), 1, "float")
        c = rt.component_wise("clamp", rt.binary("/", _u_contrast, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<", c, rt.f(0.5)):
            return rt.component_wise("mix", rt.f(0.5), shaped, rt.binary("*", c, rt.f(2.0), 1, "float"), width=1)
        return rt.component_wise("mix", shaped, s_curve01__float(shaped), rt.binary("*", rt.binary("-", c, rt.f(0.5), 1, "float"), rt.f(2.0), 1, "float"), width=1)
    def main__void():
        base_color = rt.texture(_u_inputTex, ctx.uv)
        dims = rt.construct(2, rt.texture_size(_u_inputTex))
        pixel_step = rt.binary("/", rt.f(1.0), dims, 2, "float")
        a = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<=", a, rt.f(0.0)):
            g.fragColor = base_color
            return
        if rt.binary(">=", _u_MODE, rt.i(5)):
            globalDims = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else dims)
            globalPixel = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
            materialMotion = rt.binary("*", _u_time, rt.construct(1, g.Z_LOOP), 1, "float")
            r = shape_material__float(material_value__vec2_vec2_vec2_float_uint(globalPixel, globalDims, ctx.uv, materialMotion, rt.i(305441741)))
            material = rt.construct(3, r)
            if (not (_u_mono)):
                material = rt.assign_swizzle(material, "g", shape_material__float(material_value__vec2_vec2_vec2_float_uint(globalPixel, globalDims, ctx.uv, materialMotion, rt.i(1757159915))))
                material = rt.assign_swizzle(material, "b", shape_material__float(material_value__vec2_vec2_vec2_float_uint(globalPixel, globalDims, ctx.uv, materialMotion, rt.i(48610963))))
            g.fragColor = rt.construct(4, rt.component_wise("clamp", rt.component_wise("mix", rt.swizzle(base_color, "rgb"), material, a, width=3), rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(base_color, "a"))
            return
        if rt.binary("==", _u_MODE, rt.i(4)):
            freq_scale = rt.f(48.0)
        else:
            freq_scale = rt.f(24.0)
        base_freq = freq_for_shape__float_vec2(rt.binary("*", freq_scale, rt.binary("-", rt.f(10.01), _u_scale, 1, "float"), 1, "float"), dims)
        motion = rt.binary("*", _u_time, rt.construct(1, g.Z_LOOP), 1, "float")
        h_center = height_field__vec2_vec2_float(ctx.uv, base_freq, motion)
        h_right = height_field__vec2_vec2_float(rt.binary("+", ctx.uv, rt.construct(2, rt.swizzle(pixel_step, "x"), rt.f(0.0)), 2, "float"), base_freq, motion)
        h_left = height_field__vec2_vec2_float(rt.binary("-", ctx.uv, rt.construct(2, rt.swizzle(pixel_step, "x"), rt.f(0.0)), 2, "float"), base_freq, motion)
        h_up = height_field__vec2_vec2_float(rt.binary("+", ctx.uv, rt.construct(2, rt.f(0.0), rt.swizzle(pixel_step, "y")), 2, "float"), base_freq, motion)
        h_down = height_field__vec2_vec2_float(rt.binary("-", ctx.uv, rt.construct(2, rt.f(0.0), rt.swizzle(pixel_step, "y")), 2, "float"), base_freq, motion)
        gx = rt.binary("-", h_right, h_left, 1, "float")
        gy = rt.binary("-", h_down, h_up, 1, "float")
        gradient = rt.component_wise("sqrt", rt.binary("+", rt.binary("*", gx, gx, 1, "float"), rt.binary("*", gy, gy, 1, "float"), 1, "float"), width=1)
        if rt.binary("==", _u_MODE, rt.i(4)):
            gain = rt.binary("*", g.SHADE_GAIN, rt.f(0.5), 1, "float")
        else:
            gain = rt.binary("*", g.SHADE_GAIN, rt.f(0.25), 1, "float")
        shade_base = clamp01__float(rt.binary("*", gradient, gain, 1, "float"))
        highlight_mix = clamp01__float(rt.binary("*", rt.binary("*", shade_base, shade_base, 1, "float"), rt.f(1.25), 1, "float"))
        base_factor = rt.binary("+", rt.f(0.9), rt.binary("*", h_center, rt.f(0.35), 1, "float"), 1, "float")
        factor = rt.component_wise("clamp", rt.binary("+", base_factor, rt.binary("*", highlight_mix, rt.f(0.35), 1, "float"), 1, "float"), rt.f(0.85), rt.f(1.6), width=1)
        scaled_rgb = rt.component_wise("clamp", rt.binary("*", rt.swizzle(base_color, "rgb"), factor, 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
        g.fragColor = rt.construct(4, rt.component_wise("mix", rt.swizzle(base_color, "rgb"), scaled_rgb, a, width=3), rt.swizzle(base_color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
