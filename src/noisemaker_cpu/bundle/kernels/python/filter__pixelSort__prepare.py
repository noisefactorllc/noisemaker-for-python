def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_angled = U.get("angled", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_darkest = U.get("darkest", False)
    _u_wrap = U.get("wrap", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.PI = rt.f(3.141592653589793)
    def applyWrap__vec2_vec2(coord, size):
        coord = rt.copy(coord, "float")
        size = rt.copy(size, "float")
        uv = rt.binary("/", coord, size, 2, "float")
        mode = rt.construct(1, _u_wrap, base="int")
        if rt.binary("==", mode, rt.i(0)):
            uv[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", mode, rt.i(1)):
                uv[:] = rt.component_wise("fract", uv, width=2)
            else:
                uv[:] = rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        return uv
    def main__void():
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        center = rt.binary("*", texSize, rt.f(0.5), 2, "float")
        pixelCoord = rt.binary("-", rt.swizzle(ctx.frag_coord, "xy"), center, 2, "float")
        angle = _u_angled
        rad = rt.binary("/", rt.binary("*", angle, g.PI, 1, "float"), rt.f(180.0), 1, "float")
        c = rt.component_wise("cos", rad, width=1)
        s = rt.component_wise("sin", rad, width=1)
        srcCoord = rt.construct(2, 0.0)
        srcCoord = rt.assign_swizzle(srcCoord, "x", rt.binary("+", rt.binary("*", c, rt.swizzle(pixelCoord, "x"), 1, "float"), rt.binary("*", s, rt.swizzle(pixelCoord, "y"), 1, "float"), 1, "float"))
        srcCoord = rt.assign_swizzle(srcCoord, "y", rt.binary("+", rt.binary("*", rt.unary("-", s), rt.swizzle(pixelCoord, "x"), 1, "float"), rt.binary("*", c, rt.swizzle(pixelCoord, "y"), 1, "float"), 1, "float"))
        srcCoord[:] = rt.binary("+", srcCoord, center, 2, "float")
        wrappedUV = applyWrap__vec2_vec2(srcCoord, texSize)
        color = rt.texture(_u_inputTex, wrappedUV)
        if _u_darkest:
            color[:] = rt.construct(4, rt.binary("-", rt.construct(3, rt.f(1.0)), rt.swizzle(color, "rgb"), 3, "float"), rt.swizzle(color, "a"))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
