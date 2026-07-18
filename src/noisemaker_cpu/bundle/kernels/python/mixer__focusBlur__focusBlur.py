def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_focalDistance = U.get("focalDistance", rt.f(0.0))
    _u_aperture = U.get("aperture", rt.f(0.0))
    _u_sampleBias = U.get("sampleBias", rt.f(0.0))
    _u_depthSource = U.get("depthSource", 0)
    g.fragColor = rt.construct(4, 0.0)
    def getLuminosity__vec3(color):
        color = rt.copy(color, "float")
        return rt.dot(color, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def computeBlurFactor__float(depth):
        focalPlane = rt.binary("*", _u_focalDistance, rt.f(0.01), 1, "float")
        blur = rt.binary("*", rt.component_wise("abs", rt.binary("-", depth, focalPlane, 1, "float"), width=1), _u_aperture, 1, "float")
        return rt.component_wise("clamp", blur, rt.f(0.0), rt.f(1.0), width=1)
    def applyFocusBlur__sampler2D_sampler2D_vec2(sceneTex, depthTex, uv):
        uv = rt.copy(uv, "float")
        depthSample = rt.texture(depthTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(depthTex)), 2, "float"))
        depth = getLuminosity__vec3(rt.swizzle(depthSample, "rgb"))
        blurRadius = rt.binary("*", computeBlurFactor__float(depth), _u_sampleBias, 1, "float")
        color = rt.construct(4, rt.f(0.0))
        GOLDEN = rt.f(2.399963)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(64))):
                break
            r = rt.component_wise("sqrt", rt.binary("/", rt.construct(1, i), rt.f(64.0), 1, "float"), width=1)
            theta = rt.binary("*", rt.construct(1, i), GOLDEN, 1, "float")
            offset = rt.binary("/", rt.binary("*", rt.binary("*", rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1)), r, 2, "float"), blurRadius, 2, "float"), _u_resolution, 2, "float")
            color[:] = rt.binary("+", color, rt.texture(sceneTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, offset, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(sceneTex)), 2, "float")), 4, "float")
        return rt.binary("/", color, rt.f(64.0), 4, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color = rt.construct(4, 0.0)
        if rt.binary("==", _u_depthSource, rt.i(0)):
            color[:] = applyFocusBlur__sampler2D_sampler2D_vec2(_u_tex, _u_inputTex, uv)
        else:
            color[:] = applyFocusBlur__sampler2D_sampler2D_vec2(_u_inputTex, _u_tex, uv)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "a"), rt.swizzle(rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float")), "a"), width=1))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
