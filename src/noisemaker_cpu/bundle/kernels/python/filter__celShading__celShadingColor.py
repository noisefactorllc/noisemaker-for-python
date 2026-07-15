def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_levels = U["levels"]
    _u_gamma = U["gamma"]
    _u_antialias = U["antialias"]
    _u_lightDirection = U["lightDirection"]
    _u_strength = U["strength"]
    g.MIN_GAMMA = rt.f(1e-3)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def srgb_to_linear_component__float(value):
        if rt.binary("<=", value, rt.f(0.04045)):
            return rt.binary("/", value, rt.f(12.92), 1)
        return rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1), rt.f(1.055), 1), rt.f(2.4), width=1)
    def linear_to_srgb_component__float(value):
        if rt.binary("<=", value, rt.f(0.0031308)):
            return rt.binary("*", value, rt.f(12.92), 1)
        return rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", value, rt.binary("/", rt.f(1.0), rt.f(2.4), 1), width=1), 1), rt.f(0.055), 1)
    def srgb_to_linear_rgb__vec3(rgb):
        rgb = rt.copy(rgb)
        return rt.construct(3, srgb_to_linear_component__float(rt.swizzle(rgb, "x")), srgb_to_linear_component__float(rt.swizzle(rgb, "y")), srgb_to_linear_component__float(rt.swizzle(rgb, "z")))
    def linear_to_srgb_rgb__vec3(rgb):
        rgb = rt.copy(rgb)
        return rt.construct(3, linear_to_srgb_component__float(rt.swizzle(rgb, "x")), linear_to_srgb_component__float(rt.swizzle(rgb, "y")), linear_to_srgb_component__float(rt.swizzle(rgb, "z")))
    def pow_vec3__vec3_float(value, exponent):
        value = rt.copy(value)
        return rt.construct(3, rt.component_wise("pow", rt.swizzle(value, "x"), exponent, width=1), rt.component_wise("pow", rt.swizzle(value, "y"), exponent, width=1), rt.component_wise("pow", rt.swizzle(value, "z"), exponent, width=1))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        origColor = rt.texture(_u_inputTex, uv)
        lev = _u_levels
        lightDir = rt.normalize(_u_lightDirection)
        gradientShade = rt.dot(rt.normalize(rt.construct(3, rt.binary("-", uv, rt.f(0.5), 2), rt.f(0.5))), lightDir)
        diffuse = rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), gradientShade, 1), 1)
        shadeFactor = rt.component_wise("mix", rt.f(1.0), rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), diffuse, 1), 1), _u_strength, width=1)
        shadedColor = rt.binary("*", rt.swizzle(origColor, "rgb"), shadeFactor, 3)
        gamma_value = rt.component_wise("max", _u_gamma, g.MIN_GAMMA, width=1)
        inv_gamma = rt.binary("/", rt.f(1.0), gamma_value, 1)
        inv_factor = rt.binary("/", rt.f(1.0), lev, 1)
        half_step = rt.binary("*", inv_factor, rt.f(0.5), 1)
        working_rgb = srgb_to_linear_rgb__vec3(shadedColor)
        working_rgb = pow_vec3__vec3_float(rt.component_wise("clamp", working_rgb, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3), gamma_value)
        scaled = rt.binary("+", rt.binary("*", working_rgb, lev, 3), rt.construct(3, half_step), 3)
        quantized_rgb = rt.construct(3, 0.0)
        if _u_antialias:
            f = rt.component_wise("fract", scaled, width=3)
            fw = rt.component_wise("fwidth", scaled, width=3)
            blend = rt.component_wise("smoothstep", rt.binary("-", rt.f(0.5), rt.binary("*", fw, rt.f(0.5), 3), 3), rt.binary("+", rt.f(0.5), rt.binary("*", fw, rt.f(0.5), 3), 3), f, width=3)
            quantized_rgb = rt.binary("*", rt.binary("+", rt.component_wise("floor", scaled, width=3), blend, 3), inv_factor, 3)
        else:
            quantized_rgb = rt.binary("*", rt.component_wise("floor", scaled, width=3), inv_factor, 3)
        quantized_rgb = pow_vec3__vec3_float(rt.component_wise("clamp", quantized_rgb, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3), inv_gamma)
        quantized_rgb = linear_to_srgb_rgb__vec3(quantized_rgb)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", quantized_rgb, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(origColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
