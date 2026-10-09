def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_audioSpectrum = U.get("audioSpectrum", rt.f(0.0))
    _u_lineColor = U.get("lineColor", rt.construct(3, 0.0))
    _u_lineThickness = U.get("lineThickness", rt.f(0.0))
    _u_gain = U.get("gain", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, 'float'))
        uv = rt.construct(2, rt.binary("/", globalCoord, _u_fullResolution, 2, 'float'))
        fIndex = rt.binary("*", rt.swizzle(uv, "x"), rt.f(127.0), 1, "float")
        i0 = rt.construct(1, rt.component_wise("floor", fIndex, width=1), base="int")
        i1 = rt.component_wise("min", rt.binary("+", i0, rt.i(1), 1, "int"), rt.i(127), width=1)
        fract_i = rt.component_wise("fract", fIndex, width=1)
        s0 = _u_audioSpectrum[int(i0)]
        s1 = _u_audioSpectrum[int(i1)]
        mag = rt.binary("*", rt.component_wise("mix", s0, s1, fract_i, width=1), _u_gain, 1, "float")
        dist = rt.binary("*", rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "y"), mag, 1, "float"), width=1), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        line = rt.component_wise("smoothstep", rt.binary("+", _u_lineThickness, rt.f(1.0), 1, "float"), _u_lineThickness, dist, width=1)
        fill = rt.binary("*", rt.component_wise("smoothstep", rt.binary("+", mag, rt.binary("/", rt.f(1.0), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), mag, rt.swizzle(uv, "y"), width=1), rt.f(0.15), 1, "float")
        alpha = rt.component_wise("max", line, fill, width=1)
        g.fragColor[:] = rt.construct(4, rt.binary("*", _u_lineColor, alpha, 3, 'float'), alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
