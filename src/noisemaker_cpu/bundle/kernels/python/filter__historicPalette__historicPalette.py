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
    _u_paletteIndex = U["paletteIndex"]
    _u_smoothness = U["smoothness"]
    _u_rotation = U["rotation"]
    _u_offset = U["offset"]
    _u_repeat = U["repeat"]
    _u_alpha = U["alpha"]
    _u_time = U["time"]
    g.PALETTE_COUNT = rt.i(21)
    g.PALETTES = rt.array([[rt.construct(3, rt.f(0.165), rt.f(0.102), rt.f(0.039)), rt.construct(3, rt.f(0.914), rt.f(0.769), rt.f(0.416)), rt.construct(3, rt.f(0.627), rt.f(0.322), rt.f(0.176)), rt.construct(3, rt.f(0.957), rt.f(0.894), rt.f(0.843)), rt.construct(3, rt.f(0.545), rt.f(0.271), rt.f(0.075))], [rt.construct(3, rt.f(0.306), rt.f(0.204), rt.f(0.18)), rt.construct(3, rt.f(0.827), rt.f(0.184), rt.f(0.184)), rt.construct(3, rt.f(0.98), rt.f(0.98), rt.f(0.98)), rt.construct(3, rt.f(0.098), rt.f(0.463), rt.f(0.824)), rt.construct(3, rt.f(0.976), rt.f(0.659), rt.f(0.145))], [rt.construct(3, rt.f(0.039), rt.f(0.039), rt.f(0.039)), rt.construct(3, rt.f(0.831), rt.f(0.686), rt.f(0.216)), rt.construct(3, rt.f(0.173), rt.f(0.373), rt.f(0.435)), rt.construct(3, rt.f(0.961), rt.f(0.961), rt.f(0.863)), rt.construct(3, rt.f(0.769), rt.f(0.118), rt.f(0.227))], [rt.construct(3, rt.f(0.361), rt.f(0.514), rt.f(0.455)), rt.construct(3, rt.f(0.659), rt.f(0.776), rt.f(0.525)), rt.construct(3, rt.f(0.957), rt.f(0.894), rt.f(0.757)), rt.construct(3, rt.f(0.91), rt.f(0.706), rt.f(0.627)), rt.construct(3, rt.f(0.608), rt.f(0.494), rt.f(0.741))], [rt.construct(3, rt.f(0.102), rt.f(0.102), rt.f(0.102)), rt.construct(3, rt.f(0.969), rt.f(0.925), rt.f(0.075)), rt.construct(3, rt.f(0.059), rt.f(0.278), rt.f(0.686)), rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(1.0)), rt.construct(3, rt.f(0.89), rt.f(0.118), rt.f(0.141))], [rt.construct(3, rt.f(0.173), rt.f(0.094), rt.f(0.063)), rt.construct(3, rt.f(0.871), rt.f(0.722), rt.f(0.529)), rt.construct(3, rt.f(0.545), rt.f(0.271), rt.f(0.075)), rt.construct(3, rt.f(0.961), rt.f(0.902), rt.f(0.827)), rt.construct(3, rt.f(0.824), rt.f(0.412), rt.f(0.118))], [rt.construct(3, rt.f(0.102), rt.f(0.102), rt.f(0.102)), rt.construct(3, rt.f(0.29), rt.f(0.29), rt.f(0.29)), rt.construct(3, rt.f(0.502), rt.f(0.502), rt.f(0.502)), rt.construct(3, rt.f(0.749), rt.f(0.749), rt.f(0.749)), rt.construct(3, rt.f(0.961), rt.f(0.961), rt.f(0.941))], [rt.construct(3, rt.f(0.29), rt.f(0.055), rt.f(0.055)), rt.construct(3, rt.f(0.553), rt.f(0.431), rt.f(0.388)), rt.construct(3, rt.f(0.243), rt.f(0.149), rt.f(0.137)), rt.construct(3, rt.f(0.831), rt.f(0.647), rt.f(0.455)), rt.construct(3, rt.f(0.106), rt.f(0.369), rt.f(0.125))], [rt.construct(3, rt.f(0.482), rt.f(0.176), rt.f(0.149)), rt.construct(3, rt.f(0.361), rt.f(0.294), rt.f(0.6)), rt.construct(3, rt.f(0.29), rt.f(0.486), rt.f(0.349)), rt.construct(3, rt.f(0.957), rt.f(0.635), rt.f(0.38)), rt.construct(3, rt.f(1.0), rt.f(0.42), rt.f(0.208))], [rt.construct(3, rt.f(0.722), rt.f(0.651), rt.f(0.851)), rt.construct(3, rt.f(0.769), rt.f(0.91), rt.f(0.761)), rt.construct(3, rt.f(0.91), rt.f(0.769), rt.f(0.627)), rt.construct(3, rt.f(0.902), rt.f(0.835), rt.f(0.722)), rt.construct(3, rt.f(0.659), rt.f(0.847), rt.f(0.918))], [rt.construct(3, rt.f(0.082), rt.f(0.263), rt.f(0.376)), rt.construct(3, rt.f(0.118), rt.f(0.518), rt.f(0.286)), rt.construct(3, rt.f(0.769), rt.f(0.118), rt.f(0.227)), rt.construct(3, rt.f(0.953), rt.f(0.612), rt.f(0.071)), rt.construct(3, rt.f(0.988), rt.f(0.953), rt.f(0.812))], [rt.construct(3, rt.f(0.0), rt.f(0.306), rt.f(0.537)), rt.construct(3, rt.f(0.0), rt.f(0.549), rt.f(0.549)), rt.construct(3, rt.f(0.831), rt.f(0.686), rt.f(0.216)), rt.construct(3, rt.f(0.545), rt.f(0.0), rt.f(0.0)), rt.construct(3, rt.f(0.973), rt.f(0.973), rt.f(0.941))], [rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.construct(3, rt.f(0.0), rt.f(0.322), rt.f(0.647)), rt.construct(3, rt.f(0.808), rt.f(0.067), rt.f(0.149)), rt.construct(3, rt.f(0.0), rt.f(0.62), rt.f(0.286)), rt.construct(3, rt.f(0.992), rt.f(0.725), rt.f(0.075))], [rt.construct(3, rt.f(0.173), rt.f(0.094), rt.f(0.063)), rt.construct(3, rt.f(0.824), rt.f(0.706), rt.f(0.549)), rt.construct(3, rt.f(0.396), rt.f(0.263), rt.f(0.129)), rt.construct(3, rt.f(0.961), rt.f(0.961), rt.f(0.863)), rt.construct(3, rt.f(0.545), rt.f(0.271), rt.f(0.075))], [rt.construct(3, rt.f(0.004), rt.f(0.341), rt.f(0.608)), rt.construct(3, rt.f(0.847), rt.f(0.263), rt.f(0.082)), rt.construct(3, rt.f(0.337), rt.f(0.545), rt.f(0.184)), rt.construct(3, rt.f(0.365), rt.f(0.251), rt.f(0.216)), rt.construct(3, rt.f(0.976), rt.f(0.659), rt.f(0.145))], [rt.construct(3, rt.f(0.259), rt.f(0.259), rt.f(0.259)), rt.construct(3, rt.f(0.62), rt.f(0.62), rt.f(0.62)), rt.construct(3, rt.f(0.11), rt.f(0.11), rt.f(0.11)), rt.construct(3, rt.f(0.878), rt.f(0.878), rt.f(0.878)), rt.construct(3, rt.f(0.961), rt.f(0.961), rt.f(0.961))], [rt.construct(3, rt.f(0.608), rt.f(0.349), rt.f(0.714)), rt.construct(3, rt.f(0.086), rt.f(0.627), rt.f(0.522)), rt.construct(3, rt.f(0.906), rt.f(0.298), rt.f(0.235)), rt.construct(3, rt.f(0.953), rt.f(0.612), rt.f(0.071)), rt.construct(3, rt.f(0.925), rt.f(0.941), rt.f(0.945))], [rt.construct(3, rt.f(0.914), rt.f(0.118), rt.f(0.388)), rt.construct(3, rt.f(1.0), rt.f(0.922), rt.f(0.231)), rt.construct(3, rt.f(0.161), rt.f(0.475), rt.f(1.0)), rt.construct(3, rt.f(1.0), rt.f(0.09), rt.f(0.267)), rt.construct(3, rt.f(0.0), rt.f(0.902), rt.f(0.463))], [rt.construct(3, rt.f(0.184), rt.f(0.31), rt.f(0.184)), rt.construct(3, rt.f(0.545), rt.f(0.455), rt.f(0.333)), rt.construct(3, rt.f(0.545), rt.f(0.0), rt.f(0.0)), rt.construct(3, rt.f(0.855), rt.f(0.647), rt.f(0.125)), rt.construct(3, rt.f(0.098), rt.f(0.098), rt.f(0.439))], [rt.construct(3, rt.f(0.216), rt.f(0.278), rt.f(0.31)), rt.construct(3, rt.f(0.961), rt.f(0.486), rt.f(0.0)), rt.construct(3, rt.f(0.29), rt.f(0.078), rt.f(0.549)), rt.construct(3, rt.f(1.0), rt.f(0.878), rt.f(0.51)), rt.construct(3, rt.f(0.0), rt.f(0.412), rt.f(0.361))], [rt.construct(3, rt.f(0.118), rt.f(0.302), rt.f(0.545)), rt.construct(3, rt.f(0.91), rt.f(0.698), rt.f(0.596)), rt.construct(3, rt.f(0.176), rt.f(0.314), rt.f(0.086)), rt.construct(3, rt.f(0.957), rt.f(0.91), rt.f(0.757)), rt.construct(3, rt.f(0.769), rt.f(0.118), rt.f(0.227))]])
    def sampleHistoricPalette__struct1_float_float(pal, lum, smoothAmount):
        t1 = rt.f(0.2)
        t2 = rt.f(0.4)
        t3 = rt.f(0.6)
        t4 = rt.f(0.8)
        blendWidth = rt.binary("*", smoothAmount, rt.f(0.1), 1, "float")
        b1 = rt.component_wise("smoothstep", rt.binary("-", t1, blendWidth, 1, "float"), rt.binary("+", t1, blendWidth, 1, "float"), lum, width=1)
        b2 = rt.component_wise("smoothstep", rt.binary("-", t2, blendWidth, 1, "float"), rt.binary("+", t2, blendWidth, 1, "float"), lum, width=1)
        b3 = rt.component_wise("smoothstep", rt.binary("-", t3, blendWidth, 1, "float"), rt.binary("+", t3, blendWidth, 1, "float"), lum, width=1)
        b4 = rt.component_wise("smoothstep", rt.binary("-", t4, blendWidth, 1, "float"), rt.binary("+", t4, blendWidth, 1, "float"), lum, width=1)
        result = rt.component_wise("mix", pal[0], pal[1], b1, width=3)
        result = rt.component_wise("mix", result, pal[2], b2, width=3)
        result = rt.component_wise("mix", result, pal[3], b3, width=3)
        result = rt.component_wise("mix", result, pal[4], b4, width=3)
        if rt.binary(">", blendWidth, rt.f(0.0)):
            d = (rt.binary("-", lum, rt.f(1.0), 1, "float") if rt.binary(">", lum, rt.f(0.5)) else lum)
            wrapFactor = rt.component_wise("smoothstep", rt.unary("-", blendWidth), blendWidth, d, width=1)
            wrapColor = rt.component_wise("mix", pal[4], pal[0], wrapFactor, width=3)
            wrapMask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), blendWidth, rt.component_wise("abs", d, width=1), width=1), 1, "float")
            result = rt.component_wise("mix", result, wrapColor, wrapMask, width=3)
        return result
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2, "float")
        inputColor = rt.texture(_u_inputTex, uv)
        idx = rt.component_wise("clamp", _u_paletteIndex, rt.i(0), rt.binary("-", g.PALETTE_COUNT, rt.i(1), 1, "int"), width=1)
        lum = rt.dot(rt.swizzle(inputColor, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        t = rt.binary("+", rt.binary("*", rt.binary("*", lum, rt.binary("-", rt.f(1.0), rt.f(0.0001), 1, "float"), 1, "float"), _u_repeat, 1, "float"), rt.binary("*", _u_offset, rt.f(0.01), 1, "float"), 1, "float")
        if rt.binary("==", _u_rotation, rt.unary("-", rt.i(1))):
            t = rt.binary("+", t, _u_time, 1, "float")
        else:
            if rt.binary("==", _u_rotation, rt.i(1)):
                t = rt.binary("-", t, _u_time, 1, "float")
        t = rt.component_wise("fract", t, width=1)
        pal = g.PALETTES[int(idx)]
        paletteColor = sampleHistoricPalette__struct1_float_float(pal, t, _u_smoothness)
        blendedColor = rt.component_wise("mix", rt.swizzle(inputColor, "rgb"), paletteColor, _u_alpha, width=3)
        g.fragColor = rt.construct(4, blendedColor, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
