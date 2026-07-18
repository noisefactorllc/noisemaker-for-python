def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_paletteIndex = U.get("paletteIndex", 0)
    _u_rotation = U.get("rotation", 0)
    _u_offset = U.get("offset", rt.f(0.0))
    _u_repeat = U.get("repeat", rt.f(0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.MODE_RGB = rt.i(0)
    g.MODE_HSV = rt.i(1)
    g.MODE_OKLAB = rt.i(2)
    g.PALETTE_COUNT = rt.i(55)
    g.PALETTES = rt.array([[rt.construct(4, rt.f(0.76), rt.f(0.88), rt.f(0.37), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.93), rt.f(0.97), rt.f(0.52), rt.f(0.0)), rt.construct(4, rt.f(0.21), rt.f(0.41), rt.f(0.56), rt.f(0.0))], [rt.construct(4, rt.f(0.56851584), rt.f(0.7740668), rt.f(0.23485267), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.727029), rt.f(0.08039695), rt.f(0.10427457), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.3), rt.f(0.2), rt.f(0.2), rt.f(0.0))], [rt.construct(4, rt.f(0.45), rt.f(0.2), rt.f(0.1), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.7), rt.f(0.2), rt.f(0.2), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.4), rt.f(0.0), rt.f(0.0))], [rt.construct(4, rt.f(0.09), rt.f(0.59), rt.f(0.48), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.2), rt.f(0.31), rt.f(0.98), rt.f(0.0)), rt.construct(4, rt.f(0.88), rt.f(0.4), rt.f(0.33), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.1), rt.f(0.4), rt.f(0.7), rt.f(0.0)), rt.construct(4, rt.f(0.1), rt.f(0.1), rt.f(0.1), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.1), rt.f(0.2), rt.f(0.0))], [rt.construct(4, rt.f(0.7259015), rt.f(0.7004237), rt.f(0.9494409), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.63290054), rt.f(0.37883538), rt.f(0.29405284), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.1), rt.f(0.2), rt.f(0.0))], [rt.construct(4, rt.f(0.94), rt.f(0.33), rt.f(0.27), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.74), rt.f(0.37), rt.f(0.73), rt.f(0.0)), rt.construct(4, rt.f(0.44), rt.f(0.17), rt.f(0.88), rt.f(0.0))], [rt.construct(4, rt.f(1.0), rt.f(0.7), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(0.4), rt.f(0.9), rt.f(0.0)), rt.construct(4, rt.f(0.4), rt.f(0.5), rt.f(0.6), rt.f(0.0))], [rt.construct(4, rt.f(0.51), rt.f(0.39), rt.f(0.41), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.59), rt.f(0.53), rt.f(0.94), rt.f(0.0)), rt.construct(4, rt.f(0.15), rt.f(0.41), rt.f(0.46), rt.f(0.0))], [rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.51), rt.f(1.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.43), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.36), rt.f(0.0))], [rt.construct(4, rt.f(0.83), rt.f(0.45), rt.f(0.19), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.79), rt.f(0.45), rt.f(0.35), rt.f(0.0)), rt.construct(4, rt.f(0.28), rt.f(0.91), rt.f(0.61), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.2), rt.f(0.25), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.22), rt.f(0.48), rt.f(0.62), rt.f(0.0)), rt.construct(4, rt.f(0.1), rt.f(0.3), rt.f(0.2), rt.f(0.0))], [rt.construct(4, rt.f(0.02), rt.f(0.92), rt.f(0.76), rt.f(1.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.51), rt.f(0.49), rt.f(0.51), rt.f(0.0)), rt.construct(4, rt.f(0.71), rt.f(0.23), rt.f(0.66), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(2.0), rt.f(2.0), rt.f(2.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0))], [rt.construct(4, rt.f(0.79), rt.f(0.56), rt.f(0.22), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.96), rt.f(0.5), rt.f(0.49), rt.f(0.0)), rt.construct(4, rt.f(0.15), rt.f(0.98), rt.f(0.87), rt.f(0.0))], [rt.construct(4, rt.f(0.75804377), rt.f(0.62868536), rt.f(0.2227562), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.35536355), rt.f(0.12935615), rt.f(0.17060602), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.25), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.79), rt.f(0.5), rt.f(0.23), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.75), rt.f(0.47), rt.f(0.45), rt.f(0.0)), rt.construct(4, rt.f(0.08), rt.f(0.84), rt.f(0.16), rt.f(0.0))], [rt.construct(4, rt.f(0.7), rt.f(0.81), rt.f(0.73), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.1), rt.f(0.22), rt.f(0.27), rt.f(0.0)), rt.construct(4, rt.f(0.99), rt.f(0.12), rt.f(0.94), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(1.0), rt.f(0.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(0.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(0.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.74), rt.f(0.33), rt.f(0.09), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.62), rt.f(0.2), rt.f(0.2), rt.f(0.0)), rt.construct(4, rt.f(0.2), rt.f(0.1), rt.f(0.0), rt.f(0.0))], [rt.construct(4, rt.f(0.56), rt.f(0.68), rt.f(0.39), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.72), rt.f(0.07), rt.f(0.62), rt.f(0.0)), rt.construct(4, rt.f(0.25), rt.f(0.4), rt.f(0.41), rt.f(0.0))], [rt.construct(4, rt.f(0.78), rt.f(0.39), rt.f(0.07), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.53), rt.f(0.33), rt.f(0.0)), rt.construct(4, rt.f(0.94), rt.f(0.92), rt.f(0.9), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.2), rt.f(0.64), rt.f(0.62), rt.f(0.0)), rt.construct(4, rt.f(0.15), rt.f(0.2), rt.f(0.3), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.64), rt.f(0.12), rt.f(0.84), rt.f(0.0)), rt.construct(4, rt.f(0.1), rt.f(0.25), rt.f(0.15), rt.f(0.0))], [rt.construct(4, rt.f(0.42), rt.f(0.42), rt.f(0.04), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.47), rt.f(0.27), rt.f(0.27), rt.f(0.0)), rt.construct(4, rt.f(0.41), rt.f(0.14), rt.f(0.11), rt.f(0.0))], [rt.construct(4, rt.f(0.65), rt.f(0.4), rt.f(0.11), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.72), rt.f(0.45), rt.f(0.08), rt.f(0.0)), rt.construct(4, rt.f(0.71), rt.f(0.8), rt.f(0.84), rt.f(0.0))], [rt.construct(4, rt.f(0.62), rt.f(0.79), rt.f(0.11), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.22), rt.f(0.56), rt.f(0.17), rt.f(0.0)), rt.construct(4, rt.f(0.15), rt.f(0.1), rt.f(0.25), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.41), rt.f(0.22), rt.f(0.67), rt.f(0.0)), rt.construct(4, rt.f(0.2), rt.f(0.25), rt.f(0.2), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.25), rt.f(0.5), rt.f(0.75), rt.f(0.0))], [rt.construct(4, rt.f(0.6059281), rt.f(0.17591387), rt.f(0.17166573), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.5224456), rt.f(0.3864609), rt.f(0.36020845), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.25), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.6059281), rt.f(0.17591387), rt.f(0.17166573), rt.f(0.0)), rt.construct(4, rt.f(2.0), rt.f(2.0), rt.f(2.0), rt.f(0.0)), rt.construct(4, rt.f(0.5224456), rt.f(0.3864609), rt.f(0.36020845), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.25), rt.f(0.5), rt.f(0.0))], [rt.construct(4, rt.f(0.42), rt.f(0.0), rt.f(0.0), rt.f(2.0)), rt.construct(4, rt.f(2.0), rt.f(2.0), rt.f(2.0), rt.f(0.0)), rt.construct(4, rt.f(0.45), rt.f(0.5), rt.f(0.42), rt.f(0.0)), rt.construct(4, rt.f(0.63), rt.f(1.0), rt.f(1.0), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.83), rt.f(0.6), rt.f(0.63), rt.f(0.0)), rt.construct(4, rt.f(0.3), rt.f(0.1), rt.f(0.0), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.6), rt.f(0.4), rt.f(0.1), rt.f(0.0)), rt.construct(4, rt.f(0.3), rt.f(0.2), rt.f(0.1), rt.f(0.0))], [rt.construct(4, rt.f(0.46), rt.f(0.73), rt.f(0.19), rt.f(2.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.27), rt.f(0.79), rt.f(0.78), rt.f(0.0)), rt.construct(4, rt.f(0.27), rt.f(0.16), rt.f(0.04), rt.f(0.0))], [rt.construct(4, rt.f(0.67), rt.f(0.25), rt.f(0.27), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.74), rt.f(0.48), rt.f(0.46), rt.f(0.0)), rt.construct(4, rt.f(0.07), rt.f(0.79), rt.f(0.39), rt.f(0.0))], [rt.construct(4, rt.f(0.9), rt.f(0.43), rt.f(0.34), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.56), rt.f(0.69), rt.f(0.32), rt.f(0.0)), rt.construct(4, rt.f(0.03), rt.f(0.8), rt.f(0.4), rt.f(0.0))], [rt.construct(4, rt.f(0.73), rt.f(0.36), rt.f(0.52), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.78), rt.f(0.68), rt.f(0.15), rt.f(0.0)), rt.construct(4, rt.f(0.74), rt.f(0.93), rt.f(0.28), rt.f(0.0))], [rt.construct(4, rt.f(1.0), rt.f(0.0), rt.f(0.8), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(0.1), rt.f(0.0))], [rt.construct(4, rt.f(1.0), rt.f(0.25), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.25), rt.f(0.0)), rt.construct(4, rt.f(0.5), rt.f(0.0), rt.f(0.0), rt.f(0.0))], [rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.26), rt.f(0.57), rt.f(0.03), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.1), rt.f(0.3), rt.f(0.0))], [rt.construct(4, rt.f(0.28), rt.f(0.08), rt.f(0.65), rt.f(2.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.48), rt.f(0.6), rt.f(0.03), rt.f(0.0)), rt.construct(4, rt.f(0.1), rt.f(0.15), rt.f(0.3), rt.f(0.0))], [rt.construct(4, rt.f(0.65), rt.f(0.93), rt.f(0.73), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.31), rt.f(0.21), rt.f(0.27), rt.f(0.0)), rt.construct(4, rt.f(0.43), rt.f(0.45), rt.f(0.48), rt.f(0.0))], [rt.construct(4, rt.f(0.9), rt.f(0.76), rt.f(0.63), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.0), rt.f(0.19), rt.f(0.68), rt.f(0.0)), rt.construct(4, rt.f(0.43), rt.f(0.23), rt.f(0.32), rt.f(0.0))], [rt.construct(4, rt.f(0.78), rt.f(0.63), rt.f(0.68), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.41), rt.f(0.03), rt.f(0.16), rt.f(0.0)), rt.construct(4, rt.f(0.81), rt.f(0.61), rt.f(0.06), rt.f(0.0))], [rt.construct(4, rt.f(0.97), rt.f(0.74), rt.f(0.23), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.97), rt.f(0.38), rt.f(0.35), rt.f(0.0)), rt.construct(4, rt.f(0.34), rt.f(0.41), rt.f(0.44), rt.f(0.0))], [rt.construct(4, rt.f(0.68), rt.f(0.79), rt.f(0.57), rt.f(0.0)), rt.construct(4, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(4, rt.f(0.56), rt.f(0.35), rt.f(0.14), rt.f(0.0)), rt.construct(4, rt.f(0.73), rt.f(0.9), rt.f(0.99), rt.f(0.0))]])
    g.TAU = rt.f(6.283185307179586)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.swizzle(hsv, "x")
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        hp = rt.binary("*", h, rt.f(6.0), 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", hp, rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if rt.binary("<", hp, rt.f(1.0)):
            rgb[:] = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("<", hp, rt.f(2.0)):
                rgb[:] = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("<", hp, rt.f(3.0)):
                    rgb[:] = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("<", hp, rt.f(4.0)):
                        rgb[:] = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("<", hp, rt.f(5.0)):
                            rgb[:] = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            rgb[:] = rt.construct(3, c, rt.f(0.0), x)
        return rt.binary("+", rgb, rt.construct(3, m), 3, "float")
    def oklab2linear__vec3(lab):
        lab = rt.copy(lab, "float")
        L = rt.swizzle(lab, "x")
        a = rt.swizzle(lab, "y")
        b = rt.swizzle(lab, "z")
        l_ = rt.binary("+", rt.binary("+", L, rt.binary("*", rt.f(0.3963377774), a, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.2158037573), b, 1, "float"), 1, "float")
        m_ = rt.binary("-", rt.binary("-", L, rt.binary("*", rt.f(0.1055613458), a, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0638541728), b, 1, "float"), 1, "float")
        s_ = rt.binary("-", rt.binary("-", L, rt.binary("*", rt.f(0.0894841775), a, 1, "float"), 1, "float"), rt.binary("*", rt.f(1.291485548), b, 1, "float"), 1, "float")
        l = rt.binary("*", rt.binary("*", l_, l_, 1, "float"), l_, 1, "float")
        m = rt.binary("*", rt.binary("*", m_, m_, 1, "float"), m_, 1, "float")
        s = rt.binary("*", rt.binary("*", s_, s_, 1, "float"), s_, 1, "float")
        return rt.construct(3, rt.binary("+", rt.binary("-", rt.binary("*", rt.f(4.0767416621), l, 1, "float"), rt.binary("*", rt.f(3.3077115913), m, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.2309699292), s, 1, "float"), 1, "float"), rt.binary("-", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(1.2684380046)), l, 1, "float"), rt.binary("*", rt.f(2.6097574011), m, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.3413193965), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.binary("*", rt.unary("-", rt.f(0.0041960863)), l, 1, "float"), rt.binary("*", rt.f(0.7034186147), m, 1, "float"), 1, "float"), rt.binary("*", rt.f(1.707614701), s, 1, "float"), 1, "float"))
    def linear2srgb__vec3(linear):
        linear = rt.copy(linear, "float")
        low = rt.binary("*", linear, rt.f(12.92), 3, "float")
        high = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", linear, rt.construct(3, rt.binary("/", rt.f(1.0), rt.f(2.4), 1, "float")), width=3), 3, "float"), rt.f(0.055), 3, "float")
        return rt.component_wise("mix", high, low, rt.component_wise("step", linear, rt.construct(3, rt.f(0.0031308)), width=3), width=3)
    def oklab2rgb__vec3(lab):
        lab = rt.copy(lab, "float")
        lab = rt.assign_swizzle(lab, "g", rt.binary("+", rt.binary("*", rt.swizzle(lab, "g"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.276), 1, "float"))
        lab = rt.assign_swizzle(lab, "b", rt.binary("+", rt.binary("*", rt.swizzle(lab, "b"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.198), 1, "float"))
        linear_rgb = oklab2linear__vec3(lab)
        return rt.component_wise("clamp", linear2srgb__vec3(linear_rgb), rt.f(0.0), rt.f(1.0), width=3)
    def cosinePalette__float_vec3_vec3_vec3_vec3(t, amp, freq, offset, phase):
        amp = rt.copy(amp, "float")
        freq = rt.copy(freq, "float")
        offset = rt.copy(offset, "float")
        phase = rt.copy(phase, "float")
        return rt.component_wise("clamp", rt.binary("+", offset, rt.binary("*", amp, rt.component_wise("cos", rt.binary("*", g.TAU, rt.binary("+", rt.binary("*", freq, t, 3, "float"), phase, 3, "float"), 3, "float"), width=3), 3, "float"), 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2, "float")
        inputColor = rt.texture(_u_inputTex, uv)
        if (bool(rt.binary("<=", _u_paletteIndex, rt.i(0))) or bool(rt.binary(">", _u_paletteIndex, g.PALETTE_COUNT))):
            g.fragColor[:] = inputColor
            return
        lum = rt.dot(rt.swizzle(inputColor, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        t = rt.binary("+", rt.binary("*", lum, _u_repeat, 1, "float"), rt.binary("*", _u_offset, rt.f(0.01), 1, "float"), 1, "float")
        if rt.binary("==", _u_rotation, rt.unary("-", rt.i(1))):
            t = rt.binary("+", t, _u_time, 1, "float")
        else:
            if rt.binary("==", _u_rotation, rt.i(1)):
                t = rt.binary("-", t, _u_time, 1, "float")
        entry = g.PALETTES[int(rt.binary("-", _u_paletteIndex, rt.i(1), 1, "int"))]
        mode = rt.construct(1, rt.swizzle(entry[0], "w"), base="int")
        paletteColor = cosinePalette__float_vec3_vec3_vec3_vec3(t, rt.swizzle(entry[0], "xyz"), rt.swizzle(entry[1], "xyz"), rt.swizzle(entry[2], "xyz"), rt.swizzle(entry[3], "xyz"))
        finalColor = rt.construct(3, 0.0)
        if rt.binary("==", mode, g.MODE_HSV):
            finalColor[:] = hsv2rgb__vec3(paletteColor)
        else:
            if rt.binary("==", mode, g.MODE_OKLAB):
                finalColor[:] = oklab2rgb__vec3(paletteColor)
            else:
                finalColor[:] = paletteColor
        blendedColor = rt.component_wise("mix", rt.swizzle(inputColor, "rgb"), finalColor, _u_alpha, width=3)
        g.fragColor[:] = rt.construct(4, blendedColor, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
