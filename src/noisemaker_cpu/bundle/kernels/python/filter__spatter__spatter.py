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
    def pcg3__uvec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        return v
    def pcg__uint(v):
        return rt.swizzle(pcg3__uvec3(rt.construct(3, v, rt.i(0), rt.i(0), base="uint")), "x")
    def hashf__uint(h):
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg3__uvec3(rt.construct(3, h, rt.i(0), rt.i(0), base="uint")), "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
    def gridVal__ivec2_uint(p, sd):
        p = rt.copy(p)
        h = pcg3__uvec3(rt.construct(3, rt.construct(1, rt.binary("+", rt.swizzle(p, "x"), rt.i(32768), 1, "int"), base="uint"), rt.construct(1, rt.binary("+", rt.swizzle(p, "y"), rt.i(32768), 1, "int"), base="uint"), sd, base="uint"))
        return rt.binary("/", rt.construct(1, rt.swizzle(h, "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
    def cubic__float_float_float_float_float(a, b, c, d, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        return rt.binary("*", rt.f(0.5), rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.f(2.0), b, 1, "float"), rt.binary("*", rt.binary("+", rt.unary("-", a), c, 1, "float"), t, 1, "float"), 1, "float"), rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), a, 1, "float"), rt.binary("*", rt.f(5.0), b, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), c, 1, "float"), 1, "float"), d, 1, "float"), t2, 1, "float"), 1, "float"), rt.binary("*", rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", a), rt.binary("*", rt.f(3.0), b, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), c, 1, "float"), 1, "float"), d, 1, "float"), t3, 1, "float"), 1, "float"), 1, "float")
    def bicubicExpGrid__vec2_uint(pos, sd):
        pos = rt.copy(pos)
        c = rt.construct(2, rt.component_wise("floor", pos, width=2), base="int")
        f = rt.component_wise("fract", pos, width=2)
        r0 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(2), rt.unary("-", rt.i(1)), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        r1 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(0), rt.i(0), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(2), rt.i(0), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        r2 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(2), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        r3 = cubic__float_float_float_float_float(rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(2), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(0), rt.i(2), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(2), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(2), rt.i(2), base="int"), 2, "int"), sd), rt.f(4.0), width=1), rt.swizzle(f, "x"))
        return rt.component_wise("clamp", cubic__float_float_float_float_float(r0, r1, r2, r3, rt.swizzle(f, "y")), rt.f(0.0), rt.f(1.0), width=1)
    def bilinearExpGrid__vec2_uint(pos, sd):
        pos = rt.copy(pos)
        c = rt.construct(2, rt.component_wise("floor", pos, width=2), base="int")
        f = rt.component_wise("fract", pos, width=2)
        v00 = rt.component_wise("pow", gridVal__ivec2_uint(c, sd), rt.f(4.0), width=1)
        v10 = rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), sd), rt.f(4.0), width=1)
        v01 = rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1)
        v11 = rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1)
        return rt.component_wise("mix", rt.component_wise("mix", v00, v10, rt.swizzle(f, "x"), width=1), rt.component_wise("mix", v01, v11, rt.swizzle(f, "x"), width=1), rt.swizzle(f, "y"), width=1)
    def cosineExpGrid__vec2_uint(pos, sd):
        pos = rt.copy(pos)
        c = rt.construct(2, rt.component_wise("floor", pos, width=2), base="int")
        f = rt.component_wise("fract", pos, width=2)
        t = rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("cos", rt.binary("*", f, rt.f(3.14159265), 2, "float"), width=2), 2, "float"), rt.f(0.5), 2, "float")
        v00 = rt.component_wise("pow", gridVal__ivec2_uint(c, sd), rt.f(4.0), width=1)
        v10 = rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), sd), rt.f(4.0), width=1)
        v01 = rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1)
        v11 = rt.component_wise("pow", gridVal__ivec2_uint(rt.binary("+", c, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), sd), rt.f(4.0), width=1)
        return rt.component_wise("mix", rt.component_wise("mix", v00, v10, rt.swizzle(t, "x"), width=1), rt.component_wise("mix", v01, v11, rt.swizzle(t, "x"), width=1), rt.swizzle(t, "y"), width=1)
    def expFbm6Bicubic__vec2_vec2_uint(uv, freq, sd):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        a = rt.f(0.0)
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_uint(rt.binary("*", uv, freq, 2, "float"), sd), rt.f(0.5), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(2.0), 2, "float"), rt.binary("+", sd, rt.i(10000), 1, "uint")), rt.f(0.25), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(4.0), 2, "float"), rt.binary("+", sd, rt.i(20000), 1, "uint")), rt.f(0.125), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(8.0), 2, "float"), rt.binary("+", sd, rt.i(30000), 1, "uint")), rt.f(0.0625), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(16.0), 2, "float"), rt.binary("+", sd, rt.i(40000), 1, "uint")), rt.f(0.03125), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bicubicExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(32.0), 2, "float"), rt.binary("+", sd, rt.i(50000), 1, "uint")), rt.f(0.015625), 1, "float"), 1, "float")
        return rt.binary("/", a, rt.f(0.984375), 1, "float")
    def expFbm4Bilinear__vec2_vec2_uint(uv, freq, sd):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        a = rt.f(0.0)
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_uint(rt.binary("*", uv, freq, 2, "float"), sd), rt.f(0.5), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(2.0), 2, "float"), rt.binary("+", sd, rt.i(10000), 1, "uint")), rt.f(0.25), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(4.0), 2, "float"), rt.binary("+", sd, rt.i(20000), 1, "uint")), rt.f(0.125), 1, "float"), 1, "float")
        a = rt.binary("+", a, rt.binary("*", bilinearExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(8.0), 2, "float"), rt.binary("+", sd, rt.i(30000), 1, "uint")), rt.f(0.0625), 1, "float"), 1, "float")
        return rt.binary("/", a, rt.f(0.9375), 1, "float")
    def expRidgedFbm3Cosine__vec2_vec2_uint(uv, freq, sd):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        a = rt.f(0.0)
        v = rt.f(0.0)
        v = cosineExpGrid__vec2_uint(rt.binary("*", uv, freq, 2, "float"), sd)
        a = rt.binary("+", a, rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), v, 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"), rt.f(0.5), 1, "float"), 1, "float")
        v = cosineExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(2.0), 2, "float"), rt.binary("+", sd, rt.i(10000), 1, "uint"))
        a = rt.binary("+", a, rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), v, 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"), rt.f(0.25), 1, "float"), 1, "float")
        v = cosineExpGrid__vec2_uint(rt.binary("*", rt.binary("*", uv, freq, 2, "float"), rt.f(4.0), 2, "float"), rt.binary("+", sd, rt.i(20000), 1, "uint"))
        a = rt.binary("+", a, rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.f(2.0), v, 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"), rt.f(0.125), 1, "float"), 1, "float")
        return rt.binary("/", a, rt.f(0.875), 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        dims = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, dims), 2, "float")
        base = rt.texture(_u_inputTex, uv)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.construct(2, dims))
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
        nUV = rt.binary("*", globalUV, rt.construct(2, aspect, rt.f(1.0)), 2, "float")
        s = rt.binary("*", rt.construct(1, _u_seed, base="uint"), rt.i(17), 1, "uint")
        smearFreq = rt.component_wise("mix", rt.f(3.0), rt.f(6.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(10), 1, "uint"))), width=1)
        dotFreq = rt.component_wise("mix", rt.f(32.0), rt.f(64.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(50), 1, "uint"))), width=1)
        speckFreq = rt.component_wise("mix", rt.f(150.0), rt.f(200.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(90), 1, "uint"))), width=1)
        ridgeFreq = rt.component_wise("mix", rt.f(2.0), rt.f(3.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(130), 1, "uint"))), width=1)
        warpFreqX = rt.component_wise("mix", rt.f(2.0), rt.f(3.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(160), 1, "uint"))), width=1)
        warpFreqY = rt.component_wise("mix", rt.f(1.0), rt.f(3.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(170), 1, "uint"))), width=1)
        warpX = bilinearExpGrid__vec2_uint(rt.binary("*", nUV, rt.construct(2, warpFreqX, warpFreqY), 2, "float"), rt.binary("+", s, rt.i(200), 1, "uint"))
        warpY = bilinearExpGrid__vec2_uint(rt.binary("*", nUV, rt.construct(2, warpFreqX, warpFreqY), 2, "float"), rt.binary("+", s, rt.i(300), 1, "uint"))
        disp = rt.binary("+", rt.f(1.0), hashf__uint(pcg__uint(rt.binary("+", s, rt.i(150), 1, "uint"))), 1, "float")
        warpedUV = rt.binary("+", nUV, rt.binary("*", rt.binary("*", rt.binary("-", rt.construct(2, warpX, warpY), rt.f(0.5), 2, "float"), disp, 2, "float"), rt.f(0.12), 2, "float"), 2, "float")
        smear = expFbm6Bicubic__vec2_vec2_uint(warpedUV, rt.construct(2, smearFreq), rt.binary("+", s, rt.i(100), 1, "uint"))
        dots = expFbm4Bilinear__vec2_vec2_uint(nUV, rt.construct(2, dotFreq), rt.binary("+", s, rt.i(43), 1, "uint"))
        dots = rt.component_wise("clamp", rt.binary("-", rt.binary("*", rt.f(4.0), dots, 1, "float"), rt.f(1.6), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        specks = expFbm4Bilinear__vec2_vec2_uint(nUV, rt.construct(2, speckFreq), rt.binary("+", s, rt.i(71), 1, "uint"))
        specks = rt.component_wise("clamp", rt.binary("-", rt.binary("*", rt.f(4.0), specks, 1, "float"), rt.f(2.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        combined = rt.component_wise("max", smear, rt.component_wise("max", dots, specks, width=1), width=1)
        ridge = expRidgedFbm3Cosine__vec2_vec2_uint(nUV, rt.construct(2, ridgeFreq), rt.binary("+", s, rt.i(89), 1, "uint"))
        combined = rt.component_wise("max", rt.f(0.0), rt.binary("-", combined, ridge, 1, "float"), width=1)
        combined = rt.binary("*", combined, rt.binary("+", rt.f(0.5), rt.binary("*", _u_density, rt.f(2.0), 1, "float"), 1, "float"), 1, "float")
        mask = rt.component_wise("step", rt.f(0.5), combined, width=1)
        colored = rt.binary("*", rt.swizzle(base, "rgb"), _u_color, 3, "float")
        result = rt.component_wise("mix", rt.swizzle(base, "rgb"), rt.component_wise("mix", rt.swizzle(base, "rgb"), colored, mask, width=3), _u_alpha, width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
