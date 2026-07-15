def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_heightMap = T["heightMap"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_direction = U["direction"]
    _u_pivot = U["pivot"]
    g.MARCH_STEPS = rt.i(32)
    g.SHIFT_SCALE = rt.f(0.15)
    def getLuminosity__vec3(color):
        color = rt.copy(color)
        return rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def getHeight__vec2(uv):
        uv = rt.copy(uv)
        mapSize = rt.construct(2, rt.texture_size(_u_heightMap))
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2), _u_tileOffset, 2), mapSize, 2)
        return getLuminosity__vec3(rt.swizzle(rt.texture(_u_heightMap, localUV), "rgb"))
    def getInput__vec2(uv):
        uv = rt.copy(uv)
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2), _u_tileOffset, 2), texSize, 2)
        return rt.texture(_u_inputTex, localUV)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        v = (rt.normalize(_u_direction) if rt.binary(">", rt.length(_u_direction), rt.f(0.0)) else rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0)))
        shift = rt.binary("*", rt.swizzle(v, "xy"), g.SHIFT_SCALE, 2)
        isTileRendering = rt.binary(">", rt.length(_u_tileOffset), rt.f(0.0))
        if isTileRendering:
            maxDispPixels = rt.f(256.0)
            dispPixels = rt.length(rt.binary("*", shift, _u_fullResolution, 2))
            if rt.binary(">", dispPixels, maxDispPixels):
                shift = rt.binary("*", shift, rt.binary("/", maxDispPixels, dispPixels, 1), 2)
        t = rt.f(1.0)
        rayUV = rt.binary("+", uv, rt.binary("*", shift, rt.binary("-", rt.f(1.0), _u_pivot, 1), 2), 2)
        f = rt.binary("-", t, getHeight__vec2(rayUV), 1)
        if rt.binary(">", f, rt.f(0.0)):
            stepSize = rt.binary("/", rt.f(1.0), g.MARCH_STEPS, 1)
            i = rt.i(1)
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    i = rt.binary("+", i, rt.i(1), 1)
                _for0_first = False
                if not (rt.binary("<=", i, g.MARCH_STEPS)):
                    break
                prevF = f
                prevUV = rayUV
                t = rt.binary("-", rt.f(1.0), rt.binary("*", i, stepSize, 1), 1)
                rayUV = rt.binary("+", uv, rt.binary("*", shift, rt.binary("-", t, _u_pivot, 1), 2), 2)
                f = rt.binary("-", t, getHeight__vec2(rayUV), 1)
                if rt.binary("<=", f, rt.f(0.0)):
                    w = rt.binary("/", f, rt.binary("-", f, prevF, 1), 1)
                    rayUV = rt.component_wise("mix", rayUV, prevUV, w, width=2)
                    break
        g.fragColor = getInput__vec2(rayUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
