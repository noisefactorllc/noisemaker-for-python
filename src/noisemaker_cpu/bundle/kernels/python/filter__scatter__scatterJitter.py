def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_radius = U.get("radius", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    g.fragColor = rt.construct(4, 0.0)
    def pcg3d__uvec3(v_in):
        v_in = rt.copy(v_in, "uint")
        v = rt.binary("+", rt.binary("*", v_in, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        ((_vector_write_0_0 := rt.swizzle(rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint"), "x")), (_vector_write_0_1 := rt.swizzle(rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint"), "y")), (_vector_write_0_2 := rt.swizzle(rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint"), "z")), v.__setitem__(0, _vector_write_0_0), v.__setitem__(1, _vector_write_0_1), v.__setitem__(2, _vector_write_0_2), v)[-1]
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradient__vec2(uv):
        uv = rt.copy(uv, "float")
        px = rt.construct(2, rt.fdiv(rt.f(1.0), _u_resolution, 2))
        tl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2, 'float'), 2, 'float')), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2, 'float'), 2, 'float')), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2, 'float'), 2, 'float')), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.f(1.0), rt.f(1.0)), 2, 'float'), 2, 'float')), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.f(1.0), rt.f(0.0)), 2, 'float'), 2, 'float')), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2, 'float'), 2, 'float')), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.f(0.0), rt.f(1.0)), 2, 'float'), 2, 'float')), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct_raw(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2, 'float'), 2, 'float')), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1, "float"), 1, "float"), br, 1, "float"), tl, 1, "float"), rt.binary("*", rt.f(2.0), l, 1, "float"), 1, "float"), bl, 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), tr, 1, "float"), bl, 1, "float"), rt.binary("*", rt.f(2.0), b, 1, "float"), 1, "float"), br, 1, "float"))
    def main__void():
        uv = rt.construct(2, rt.fdiv(rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2))
        texel = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        texSize = rt.texture_size(_u_inputTex)
        globalCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, 'float'))
        hashCoord = rt.copy_decl(globalCoord, "float")
        if rt.binary("==", _u_MODE, rt.i(4)):
            hashCoord[:] = rt.construct(2, rt.binary("*", rt.component_wise("floor", rt.binary("/", globalCoord, rt.f(3.0), 2, 'float'), width=2), rt.f(3.0), 2, 'float'))
        h = rt.pcg3d(rt.construct(3, rt.construct(2, rt.construct(2, rt.component_wise("floor", hashCoord, width=2), base="int"), base="uint"), rt.construct(1, _u_seed, base="uint"), base="uint"))
        r256 = rt.construct(1, rt.binary("*", rt.component_wise("min", rt.component_wise("abs", _u_radius, width=1), rt.f(128.0), width=1), rt.f(256.0), 1, "float"), base="uint")
        steps = rt.binary(">>", rt.binary("*", rt.binary(">>", rt.swizzle(h, "xy"), rt.construct(2, rt.i(16), base="uint"), 2, "uint"), rt.binary("*", rt.i(2), r256, 1, "uint"), 2, "uint"), rt.construct(2, rt.i(16), base="uint"), 2, "uint")
        offset = rt.construct(2, rt.binary("/", rt.construct_raw(2, rt.construct(2, rt.binary("-", rt.construct(2, steps, base="int"), rt.construct(1, r256, base="int"), 2, "int"))), rt.f(256.0), 2, 'float'))
        grad = rt.construct(2, 0.0)
        gradLen = rt.f(0.0)
        if rt.binary("==", _u_MODE, rt.i(3)):
            grad = lumGradient__vec2(uv)
            gradLen = rt.length(grad)
            perp = rt.construct(2, 0.0)
            if rt.binary(">", gradLen, rt.f(1e-05)):
                perp = rt.construct(2, rt.fdiv(rt.construct_raw(2, rt.unary("-", rt.swizzle(grad, "y")), rt.swizzle(grad, "x")), gradLen, 2))
                ((_vector_write_1_0 := rt.binary("*", rt.dot(offset, perp), rt.swizzle(perp, "x"), 1, "float")), (_vector_write_1_1 := rt.binary("*", rt.dot(offset, perp), rt.swizzle(perp, "y"), 1, "float")), offset.__setitem__(0, _vector_write_1_0), offset.__setitem__(1, _vector_write_1_1), offset)[-1]
        sampleTexel = rt.component_wise("clamp", rt.binary("+", texel, rt.construct(2, rt.component_wise("floor", rt.binary("+", offset, rt.f(0.5), 2, 'float'), width=2), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", texSize, rt.i(1), 2, "int"), width=2)
        src = rt.texel_fetch(_u_inputTex, texel, rt.i(0))
        samp = rt.texel_fetch(_u_inputTex, sampleTexel, rt.i(0))
        result = rt.copy_decl(samp, "float")
        if rt.binary("==", _u_MODE, rt.i(1)):
            result[:] = rt.component_wise("min", src, samp, width=4)
        else:
            if rt.binary("==", _u_MODE, rt.i(2)):
                result[:] = rt.component_wise("max", src, samp, width=4)
        g.fragColor[:] = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
