def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_mapSource = U["mapSource"]
    _u_channel = U["channel"]
    _u_scale = U["scale"]
    _u_offset = U["offset"]
    _u_wrap = U["wrap"]
    g.fragColor = rt.construct(4, 0.0)
    def mirrorWrap__float(t):
        m = rt.component_wise("mod", t, rt.f(2.0), width=1)
        return (rt.binary("-", rt.f(2.0), m, 1, "float") if rt.binary(">", m, rt.f(1.0)) else m)
    def applyWrap__vec2_int(uv, wrapMode):
        uv = rt.copy(uv)
        if rt.binary("==", wrapMode, rt.i(0)):
            return rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        else:
            if rt.binary("==", wrapMode, rt.i(1)):
                return rt.construct(2, mirrorWrap__float(rt.swizzle(uv, "x")), mirrorWrap__float(rt.swizzle(uv, "y")))
            else:
                return rt.component_wise("fract", uv, width=2)
    def main__void():
        localUV = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        colorA = rt.texture(_u_inputTex, localUV)
        colorB = rt.texture(_u_tex, localUV)
        mapColor = (colorA if rt.binary("==", _u_mapSource, rt.i(0)) else colorB)
        sampleFromB = (rt.i(1) if rt.binary("==", _u_mapSource, rt.i(0)) else rt.i(0))
        rawUV = rt.construct(2, 0.0)
        if rt.binary("==", _u_channel, rt.i(0)):
            rawUV = rt.swizzle(mapColor, "rg")
        else:
            if rt.binary("==", _u_channel, rt.i(1)):
                rawUV = rt.construct(2, rt.swizzle(mapColor, "r"), rt.swizzle(mapColor, "b"))
            else:
                rawUV = rt.construct(2, rt.swizzle(mapColor, "g"), rt.swizzle(mapColor, "b"))
        s = rt.binary("/", _u_scale, rt.f(100.0), 1, "float")
        remappedUV = rt.binary("+", rt.binary("*", rawUV, s, 2, "float"), _u_offset, 2, "float")
        remappedUV = applyWrap__vec2_int(remappedUV, _u_wrap)
        sampleUV = rt.binary("/", rt.binary("-", rt.binary("*", remappedUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), _u_resolution, 2, "float")
        sampleUV = rt.component_wise("fract", sampleUV, width=2)
        result = rt.construct(4, 0.0)
        if rt.binary("==", sampleFromB, rt.i(1)):
            result = rt.texture(_u_tex, sampleUV)
        else:
            result = rt.texture(_u_inputTex, sampleUV)
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
