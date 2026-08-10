def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_stride = U.get("stride", rt.f(0.0))
    _u_quantize = U.get("quantize", rt.f(0.0))
    _u_inverse = U.get("inverse", rt.f(0.0))
    _u_inputWeight = U.get("inputWeight", rt.f(0.0))
    _u_inputTex = T["inputTex"]
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    def hash2__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        x_bits = rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
        state = rt.binary("+", rt.binary("*", x_bits, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        y_bits = rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
        return rt.construct(2, rt.binary("/", rt.construct(1, x_bits), rt.f(4294967295.0), 1, "float"), rt.binary("/", rt.construct(1, y_bits), rt.f(4294967295.0), 1, "float"))
    def wrap_float__float_float(value, size):
        if rt.binary("<=", size, rt.f(0.0)):
            return rt.f(0.0)
        scaled = rt.component_wise("floor", rt.binary("/", value, size, 1, "float"), width=1)
        wrapped = rt.binary("-", value, rt.binary("*", scaled, size, 1, "float"), 1, "float")
        if rt.binary("<", wrapped, rt.f(0.0)):
            wrapped = rt.binary("+", wrapped, size, 1, "float")
        return wrapped
    def wrap_int__int_int(value, size):
        if rt.binary("<=", size, rt.i(0)):
            return rt.i(0)
        result = rt.binary("%", value, size, 1, "int")
        if rt.binary("<", result, rt.i(0)):
            result = rt.binary("+", result, size, 1, "int")
        return result
    def srgb_to_linear__float(value):
        if rt.binary("<=", value, rt.f(0.04045)):
            return rt.binary("/", value, rt.f(12.92), 1, "float")
        return rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1, "float"), rt.f(1.055), 1, "float"), rt.f(2.4), width=1)
    def cube_root__float(value):
        if rt.binary("==", value, rt.f(0.0)):
            return rt.f(0.0)
        sign_value = (rt.f(1.0) if rt.binary(">=", value, rt.f(0.0)) else rt.unary("-", rt.f(1.0)))
        return rt.binary("*", sign_value, rt.component_wise("pow", rt.component_wise("abs", value, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1), 1, "float")
    def oklab_l__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r_lin = srgb_to_linear__float(rt.component_wise("clamp", rt.swizzle(rgb, "x"), rt.f(0.0), rt.f(1.0), width=1))
        g_lin = srgb_to_linear__float(rt.component_wise("clamp", rt.swizzle(rgb, "y"), rt.f(0.0), rt.f(1.0), width=1))
        b_lin = srgb_to_linear__float(rt.component_wise("clamp", rt.swizzle(rgb, "z"), rt.f(0.0), rt.f(1.0), width=1))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.412165612), r_lin, 1, "float"), rt.binary("*", rt.f(0.536275208), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0514575653), b_lin, 1, "float"), 1, "float")
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.211859107), r_lin, 1, "float"), rt.binary("*", rt.f(0.6807189584), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.107406579), b_lin, 1, "float"), 1, "float")
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), r_lin, 1, "float"), rt.binary("*", rt.f(0.2818474174), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.6302613616), b_lin, 1, "float"), 1, "float")
        return rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), cube_root__float(l), 1, "float"), rt.binary("*", rt.f(0.793617785), cube_root__float(m), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0040720468), cube_root__float(s), 1, "float"), 1, "float")
    def fetch_texel__int_int_int_int(x, y, width, height):
        wrapped_x = wrap_int__int_int(x, width)
        wrapped_y = wrap_int__int_int(y, height)
        return rt.texel_fetch(_u_inputTex, rt.construct(2, wrapped_x, wrapped_y, base="int"), rt.i(0))
    def luminance_at__int_int_int_int(x, y, width, height):
        texel = fetch_texel__int_int_int_int(x, y, width, height)
        return oklab_l__vec3(rt.swizzle(texel, "xyz"))
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateSize = rt.texture_size(_u_xyzTex)
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        px = rt.swizzle(xyz, "x")
        py = rt.swizzle(xyz, "y")
        alive = rt.swizzle(xyz, "w")
        vx = rt.swizzle(vel, "x")
        vy = rt.swizzle(vel, "y")
        vz = rt.swizzle(vel, "z")
        seed_f = rt.swizzle(vel, "w")
        width = rt.construct(1, rt.swizzle(_u_resolution, "x"), base="int")
        height = rt.construct(1, rt.swizzle(_u_resolution, "y"), base="int")
        agent_id = rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(stateSize, "x"), 1, "int"), 1, "int"), base="uint")
        x = rt.binary("*", px, rt.swizzle(_u_resolution, "x"), 1, "float")
        y = rt.binary("*", py, rt.swizzle(_u_resolution, "y"), 1, "float")
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            return
        if rt.binary("==", seed_f, rt.f(0.0)):
            seed_f = rt.swizzle(hash2__uint(rt.binary("+", agent_id, rt.i(99999), 1, "uint")), "x")
        inertia = rt.binary("+", rt.f(0.7), rt.binary("*", seed_f, rt.f(0.3), 1, "float"), 1, "float")
        xi = wrap_int__int_int(rt.construct(1, rt.component_wise("floor", x, width=1), base="int"), width)
        yi = wrap_int__int_int(rt.construct(1, rt.component_wise("floor", y, width=1), base="int"), height)
        x1i = wrap_int__int_int(rt.binary("+", xi, rt.i(1), 1, "int"), width)
        y1i = wrap_int__int_int(rt.binary("+", yi, rt.i(1), 1, "int"), height)
        u = rt.binary("-", x, rt.component_wise("floor", x, width=1), 1, "float")
        v = rt.binary("-", y, rt.component_wise("floor", y, width=1), 1, "float")
        c00 = luminance_at__int_int_int_int(xi, yi, width, height)
        c10 = luminance_at__int_int_int_int(x1i, yi, width, height)
        c01 = luminance_at__int_int_int_int(xi, y1i, width, height)
        c11 = luminance_at__int_int_int_int(x1i, y1i, width, height)
        gx = rt.component_wise("mix", rt.binary("-", c01, c00, 1, "float"), rt.binary("-", c11, c10, 1, "float"), u, width=1)
        gy = rt.component_wise("mix", rt.binary("-", c10, c00, 1, "float"), rt.binary("-", c11, c01, 1, "float"), v, width=1)
        if rt.binary(">", _u_inverse, rt.f(0.5)):
            gx = rt.unary("-", gx)
            gy = rt.unary("-", gy)
        if rt.binary(">", _u_quantize, rt.f(0.5)):
            gx = rt.component_wise("floor", gx, width=1)
            gy = rt.component_wise("floor", gy, width=1)
        glen = rt.length(rt.construct(2, gx, gy))
        targetVx = rt.f(0.0)
        targetVy = rt.f(0.0)
        scale = rt.f(0.0)
        if rt.binary(">", glen, rt.f(1e-06)):
            scale = rt.binary("/", rt.binary("*", _u_stride, rt.f(0.1), 1, "float"), glen, 1, "float")
            targetVx = rt.binary("*", gx, scale, 1, "float")
            targetVy = rt.binary("*", gy, scale, 1, "float")
        weightBlend = rt.component_wise("clamp", rt.binary("*", _u_inputWeight, rt.f(0.01), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        blendFactor = rt.binary("*", inertia, weightBlend, 1, "float")
        vx = rt.component_wise("mix", vx, targetVx, blendFactor, width=1)
        vy = rt.component_wise("mix", vy, targetVy, blendFactor, width=1)
        x = wrap_float__float_float(rt.binary("+", x, vx, 1, "float"), rt.swizzle(_u_resolution, "x"))
        y = wrap_float__float_float(rt.binary("+", y, vy, 1, "float"), rt.swizzle(_u_resolution, "y"))
        newPx = rt.binary("/", x, rt.swizzle(_u_resolution, "x"), 1, "float")
        newPy = rt.binary("/", y, rt.swizzle(_u_resolution, "y"), 1, "float")
        normVx = rt.binary("/", vx, rt.swizzle(_u_resolution, "x"), 1, "float")
        normVy = rt.binary("/", vy, rt.swizzle(_u_resolution, "y"), 1, "float")
        g.outXYZ[:] = rt.construct(4, newPx, newPy, rt.swizzle(xyz, "z"), alive)
        g.outVel[:] = rt.construct(4, normVx, normVy, vz, seed_f)
        g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
