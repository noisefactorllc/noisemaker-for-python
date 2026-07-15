def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_color = U["color"]
    _u_density = U["density"]
    _u_alpha = U["alpha"]
    _u_seed = U["seed"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg3__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def pcg__int(v):
        return rt.swizzle(pcg3__vec3(cpu_uvec3__float_float_float(v, rt.i(0), rt.i(0))), "x")
    def hashf__int(h):
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg3__vec3(cpu_uvec3__float_float_float(h, rt.i(0), rt.i(0))), "x")), rt.f(4294967295.0), 1)
    def gridVal__ivec2_int(p, sd):
        p = rt.copy(p)
        h = pcg3__vec3(cpu_uvec3__float_float_float(rt.construct(1, rt.binary("+", rt.swizzle(p, "x"), rt.i(32768), 1)), rt.construct(1, rt.binary("+", rt.swizzle(p, "y"), rt.i(32768), 1)), sd))
        return rt.binary("/", rt.swizzle(h, "x"), rt.f(4294967295.0), 1)
    def cubic__float_float_float_float_float(a, b, c, d, t):
        t2 = rt.binary("*", t, t, 1)
        t3 = rt.binary("*", t2, t, 1)
        return rt.binary("*", rt.f(0.5), rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.f(2.0), b, 1), rt.binary("*", rt.binary("+", rt.unary("-", a), c, 1), t, 1), 1), rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), a, 1), rt.binary("*", rt.f(5.0), b, 1), 1), rt.binary("*", rt.f(4.0), c, 1), 1), d, 1), t2, 1), 1), rt.binary("*", rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", a), rt.binary("*", rt.f(3.0), b, 1), 1), rt.binary("*", rt.f(3.0), c, 1), 1), d, 1), t3, 1), 1), 1)
    def bicubicExpGrid__vec2_int(pos, sd):
        pos = rt.copy(pos)
        c = cpu_ivec2__vec2(rt.component_wise("floor", pos, width=2))
        f = rt.component_wise("fract", pos, width=2)
        r0 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1))), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(0), rt.unary("-", rt.i(1))), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.unary("-", rt.i(1))), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(2), rt.unary("-", rt.i(1))), 2), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        r1 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.i(0)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(0), rt.i(0)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(2), rt.i(0)), 2), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        r2 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.i(1)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(1)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(2), rt.i(1)), 2), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        r3 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.i(2)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(0), rt.i(2)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(2)), 2), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(2), rt.i(2)), 2), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        return rt.component_wise("clamp", cubic__float_float_float_float_float(r0, r1, r2, r3, rt.swizzle(f, "y")), rt.f(0.0), rt.f(1.0), width=1)
    def bilinearExpGrid__vec2_int(pos, sd):
        pos = rt.copy(pos)
        c = cpu_ivec2__vec2(rt.component_wise("floor", pos, width=2))
        f = rt.component_wise("fract", pos, width=2)
        v00 = rt.component_wise("pow", gridVal__ivec2_int(c, sd), rt.f(4.0), width=1)
        v10 = rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), sd), rt.f(4.0), width=1)
        v01 = rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), sd), rt.f(4.0), width=1)
        v11 = rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(1)), 2), sd), rt.f(4.0), width=1)
        return rt.component_wise("mix", rt.component_wise("mix", v00, v10, rt.swizzle(f, "x"), width=1), rt.component_wise("mix", v01, v11, rt.swizzle(f, "x"), width=1), rt.swizzle(f, "y"), width=1)
    def cosineExpGrid__vec2_int(pos, sd):
        pos = rt.copy(pos)
        c = cpu_ivec2__vec2(rt.component_wise("floor", pos, width=2))
        f = rt.component_wise("fract", pos, width=2)
        t = rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("cos", rt.binary("*", f, rt.f(3.14159265), 2), width=2), 2), rt.f(0.5), 2)
        v00 = rt.component_wise("pow", gridVal__ivec2_int(c, sd), rt.f(4.0), width=1)
        v10 = rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), sd), rt.f(4.0), width=1)
        v01 = rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), sd), rt.f(4.0), width=1)
        v11 = rt.component_wise("pow", gridVal__ivec2_int(rt.binary("+", c, cpu_ivec2__float_float(rt.i(1), rt.i(1)), 2), sd), rt.f(4.0), width=1)
        return rt.component_wise("mix", rt.component_wise("mix", v00, v10, rt.swizzle(t, "x"), width=1), rt.component_wise("mix", v01, v11, rt.swizzle(t, "x"), width=1), rt.swizzle(t, "y"), width=1)
    def expFbm6Bicubic__vec2_vec2_int(uv, freq, sd):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        a = rt.f(0.0)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_int(rt.binary("*", uv, freq, 2), sd), rt.f(0.5), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(2.0), 2), rt.binary("+", sd, rt.i(10000), 1)), rt.f(0.25), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(4.0), 2), rt.binary("+", sd, rt.i(20000), 1)), rt.f(0.125), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(8.0), 2), rt.binary("+", sd, rt.i(30000), 1)), rt.f(0.0625), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(16.0), 2), rt.binary("+", sd, rt.i(40000), 1)), rt.f(0.03125), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(32.0), 2), rt.binary("+", sd, rt.i(50000), 1)), rt.f(0.015625), 1), 1)
        return rt.binary("/", a, rt.f(0.984375), 1)
    def expFbm4Bilinear__vec2_vec2_int(uv, freq, sd):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        a = rt.f(0.0)
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_int(rt.binary("*", uv, freq, 2), sd), rt.f(0.5), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(2.0), 2), rt.binary("+", sd, rt.i(10000), 1)), rt.f(0.25), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(4.0), 2), rt.binary("+", sd, rt.i(20000), 1)), rt.f(0.125), 1), 1)
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(8.0), 2), rt.binary("+", sd, rt.i(30000), 1)), rt.f(0.0625), 1), 1)
        return rt.binary("/", a, rt.f(0.9375), 1)
    def expRidgedFbm3Cosine__vec2_vec2_int(uv, freq, sd):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        a = rt.f(0.0)
        v = rt.f(0.0)
        v = cosineExpGrid__vec2_int(rt.binary("*", uv, freq, 2), sd)
        a = rt.binary("+", a, rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), v, 1), rt.f(1.0), 1), width=1), 1), rt.f(0.5), 1), 1)
        v = cosineExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(2.0), 2), rt.binary("+", sd, rt.i(10000), 1))
        a = rt.binary("+", a, rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), v, 1), rt.f(1.0), 1), width=1), 1), rt.f(0.25), 1), 1)
        v = cosineExpGrid__vec2_int(rt.binary("*", rt.binary("*", uv, freq, 2), rt.f(4.0), 2), rt.binary("+", sd, rt.i(20000), 1))
        a = rt.binary("+", a, rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), v, 1), rt.f(1.0), 1), width=1), 1), rt.f(0.125), 1), 1)
        return rt.binary("/", a, rt.f(0.875), 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        dims = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, dims), 2)
        base = rt.texture(_u_inputTex, uv)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.construct(2, dims))
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        nUV = rt.binary("*", globalUV, rt.construct(2, aspect, rt.f(1.0)), 2)
        s = rt.binary("*", rt.construct(1, _u_seed), rt.i(17), 1)
        smearFreq = rt.component_wise("mix", rt.f(3.0), rt.f(6.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(10), 1))), width=1)
        dotFreq = rt.component_wise("mix", rt.f(32.0), rt.f(64.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(50), 1))), width=1)
        speckFreq = rt.component_wise("mix", rt.f(150.0), rt.f(200.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(90), 1))), width=1)
        ridgeFreq = rt.component_wise("mix", rt.f(2.0), rt.f(3.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(130), 1))), width=1)
        warpFreqX = rt.component_wise("mix", rt.f(2.0), rt.f(3.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(160), 1))), width=1)
        warpFreqY = rt.component_wise("mix", rt.f(1.0), rt.f(3.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(170), 1))), width=1)
        warpX = bilinearExpGrid__vec2_int(rt.binary("*", nUV, rt.construct(2, warpFreqX, warpFreqY), 2), rt.binary("+", s, rt.i(200), 1))
        warpY = bilinearExpGrid__vec2_int(rt.binary("*", nUV, rt.construct(2, warpFreqX, warpFreqY), 2), rt.binary("+", s, rt.i(300), 1))
        disp = rt.binary("+", rt.f(1.0), hashf__int(pcg__int(rt.binary("+", s, rt.i(150), 1))), 1)
        warpedUV = rt.binary("+", nUV, rt.binary("*", rt.binary("*", rt.binary("-", rt.construct(2, warpX, warpY), rt.f(0.5), 2), disp, 2), rt.f(0.12), 2), 2)
        smear = expFbm6Bicubic__vec2_vec2_int(warpedUV, rt.construct(2, smearFreq), rt.binary("+", s, rt.i(100), 1))
        dots = expFbm4Bilinear__vec2_vec2_int(nUV, rt.construct(2, dotFreq), rt.binary("+", s, rt.i(43), 1))
        dots = rt.component_wise("clamp", rt.binary("-", rt.binary("*", rt.f(4.0), dots, 1), rt.f(1.6), 1), rt.f(0.0), rt.f(1.0), width=1)
        specks = expFbm4Bilinear__vec2_vec2_int(nUV, rt.construct(2, speckFreq), rt.binary("+", s, rt.i(71), 1))
        specks = rt.component_wise("clamp", rt.binary("-", rt.binary("*", rt.f(4.0), specks, 1), rt.f(2.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        combined = rt.component_wise("max", smear, rt.component_wise("max", dots, specks, width=1), width=1)
        ridge = expRidgedFbm3Cosine__vec2_vec2_int(nUV, rt.construct(2, ridgeFreq), rt.binary("+", s, rt.i(89), 1))
        combined = rt.component_wise("max", rt.f(0.0), rt.binary("-", combined, ridge, 1), width=1)
        combined = rt.binary("*", combined, rt.binary("+", rt.f(0.5), rt.binary("*", _u_density, rt.f(2.0), 1), 1), 1)
        mask = rt.component_wise("step", rt.f(0.5), combined, width=1)
        colored = rt.binary("*", rt.swizzle(base, "rgb"), _u_color, 3)
        result = rt.component_wise("mix", rt.swizzle(base, "rgb"), rt.component_wise("mix", rt.swizzle(base, "rgb"), colored, mask, width=3), _u_alpha, width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
