def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_source = T["source"]
    _u_layer0_tex = T["layer0_tex"]
    _u_layer1_tex = T["layer1_tex"]
    _u_layer2_tex = T["layer2_tex"]
    _u_layer3_tex = T["layer3_tex"]
    _u_layer4_tex = T["layer4_tex"]
    _u_layer5_tex = T["layer5_tex"]
    _u_layer6_tex = T["layer6_tex"]
    _u_layer7_tex = T["layer7_tex"]
    _u_layers = U["layers"]
    _u_smoothness = U["smoothness"]
    _u_layer0_active = U["layer0_active"]
    _u_layer1_active = U["layer1_active"]
    _u_layer2_active = U["layer2_active"]
    _u_layer3_active = U["layer3_active"]
    _u_layer4_active = U["layer4_active"]
    _u_layer5_active = U["layer5_active"]
    _u_layer6_active = U["layer6_active"]
    _u_layer7_active = U["layer7_active"]
    def getLuminosity__vec3(color):
        color = rt.copy(color)
        return rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def sampleLayer__int_vec2(i, uv):
        uv = rt.copy(uv)
        if rt.binary("==", i, rt.i(0)):
            return rt.texture(_u_layer0_tex, uv)
        if rt.binary("==", i, rt.i(1)):
            return rt.texture(_u_layer1_tex, uv)
        if rt.binary("==", i, rt.i(2)):
            return rt.texture(_u_layer2_tex, uv)
        if rt.binary("==", i, rt.i(3)):
            return rt.texture(_u_layer3_tex, uv)
        if rt.binary("==", i, rt.i(4)):
            return rt.texture(_u_layer4_tex, uv)
        if rt.binary("==", i, rt.i(5)):
            return rt.texture(_u_layer5_tex, uv)
        if rt.binary("==", i, rt.i(6)):
            return rt.texture(_u_layer6_tex, uv)
        return rt.texture(_u_layer7_tex, uv)
    def layerActive__int(i):
        if rt.binary("==", i, rt.i(0)):
            return _u_layer0_active
        if rt.binary("==", i, rt.i(1)):
            return _u_layer1_active
        if rt.binary("==", i, rt.i(2)):
            return _u_layer2_active
        if rt.binary("==", i, rt.i(3)):
            return _u_layer3_active
        if rt.binary("==", i, rt.i(4)):
            return _u_layer4_active
        if rt.binary("==", i, rt.i(5)):
            return _u_layer5_active
        if rt.binary("==", i, rt.i(6)):
            return _u_layer6_active
        return _u_layer7_active
    def bandWeight__float_float(lum, boundary):
        if rt.binary("<=", _u_smoothness, rt.f(0.0)):
            return rt.component_wise("step", boundary, lum, width=1)
        return rt.component_wise("smoothstep", rt.binary("-", boundary, _u_smoothness, 1, "float"), rt.binary("+", boundary, _u_smoothness, 1, "float"), lum, width=1)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        controlColor = rt.texture(_u_source, uv)
        lum = getLuminosity__vec3(rt.swizzle(controlColor, "rgb"))
        n = rt.component_wise("clamp", _u_layers, rt.i(2), rt.i(8), width=1)
        result = (sampleLayer__int_vec2(rt.i(0), uv) if rt.binary("==", layerActive__int(rt.i(0)), rt.i(1)) else controlColor)
        k = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                k = rt.binary("+", k, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", k, rt.i(8))):
                break
            if rt.binary(">=", k, n):
                break
            src = (sampleLayer__int_vec2(k, uv) if rt.binary("==", layerActive__int(k), rt.i(1)) else controlColor)
            boundary = rt.binary("/", k, n, 1, "int")
            w = bandWeight__float_float(lum, boundary)
            result = rt.component_wise("mix", result, src, w, width=4)
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
