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
    _u_colorTex = T["colorTex"]
    _u_edgeTex = T["edgeTex"]
    _u_edgeColor = U["edgeColor"]
    _u_mixAmount = U["mixAmount"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        origColor = rt.texture(_u_inputTex, uv)
        celColor = rt.texture(_u_colorTex, uv)
        edgeStrength = rt.swizzle(rt.texture(_u_edgeTex, uv), "r")
        finalColor = rt.component_wise("mix", rt.swizzle(celColor, "rgb"), _u_edgeColor, edgeStrength, width=3)
        finalColor = rt.component_wise("mix", rt.swizzle(origColor, "rgb"), finalColor, _u_mixAmount, width=3)
        g.fragColor = rt.construct(4, finalColor, rt.swizzle(origColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
