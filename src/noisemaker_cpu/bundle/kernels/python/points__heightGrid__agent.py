def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_heightTex = T["heightTex"]
    _u_diffuseTex = T["diffuseTex"]
    _u_gridScale = U.get("gridScale", rt.f(0.0))
    _u_heightScale = U.get("heightScale", rt.f(0.0))
    _u_heightOffset = U.get("heightOffset", rt.f(0.0))
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateSize = rt.texture_size(_u_xyzTex)
        uv = rt.binary("/", rt.binary("+", rt.construct(2, coord), rt.f(0.5), 2, "float"), rt.construct(2, stateSize), 2, "float")
        heightColor = rt.swizzle(rt.texture(_u_heightTex, uv), "rgb")
        elevation = rt.dot(heightColor, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        g.outXYZ[:] = rt.construct(4, rt.binary("*", rt.binary("-", rt.swizzle(uv, "x"), rt.f(0.5), 1, "float"), _u_gridScale, 1, "float"), rt.binary("+", rt.binary("*", elevation, _u_heightScale, 1, "float"), _u_heightOffset, 1, "float"), rt.binary("*", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), _u_gridScale, 1, "float"), rt.f(1.0))
        g.outVel[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.swizzle(rt.texel_fetch(_u_velTex, coord, rt.i(0)), "w"))
        g.outRGBA[:] = rt.texture(_u_diffuseTex, uv)
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
