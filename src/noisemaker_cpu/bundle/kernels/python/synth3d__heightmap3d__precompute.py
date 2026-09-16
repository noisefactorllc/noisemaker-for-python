def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_heightTex = T["heightTex"]
    _u_tex = T["tex"]
    _u_volumeSize = U.get("volumeSize", 0)
    _u_heightScale = U.get("heightScale", rt.f(0.0))
    _u_baseHeight = U.get("baseHeight", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    def imageTexel__ivec2_ivec2(column, size):
        column = rt.copy(column, "int")
        size = rt.copy(size, "int")
        return rt.component_wise("clamp", rt.binary("/", rt.binary("*", rt.binary("+", rt.binary("*", column, rt.i(2), 2, "int"), rt.i(1), 2, "int"), size, 2, "int"), rt.binary("*", _u_volumeSize, rt.i(2), 1, "int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", size, rt.i(1), 2, "int"), width=2)
    def columnHeight__ivec2(column):
        column = rt.copy(column, "int")
        rgb = rt.swizzle(rt.texel_fetch(_u_heightTex, imageTexel__ivec2_ivec2(column, rt.texture_size(_u_heightTex)), rt.i(0)), "rgb")
        luminance = rt.dot(rgb, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        return rt.component_wise("floor", rt.binary("+", rt.binary("*", rt.component_wise("clamp", rt.binary("+", rt.binary("*", luminance, _u_heightScale, 1, "float"), _u_baseHeight, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.construct(1, _u_volumeSize), 1, "float"), rt.f(0.5), 1, "float"), width=1)
    def density__ivec3(p):
        p = rt.copy(p, "int")
        if (bool(rt.component_wise("any", rt.component_wise("lessThan", p, rt.construct(3, rt.i(0), base="int"), width=3), width=3)) or bool(rt.component_wise("any", rt.component_wise("greaterThanEqual", p, rt.construct(3, _u_volumeSize, base="int"), width=3), width=3))):
            return rt.f(0.0)
        return rt.construct(1, rt.binary("<", rt.construct(1, rt.swizzle(p, "y")), columnHeight__ivec2(rt.swizzle(p, "xz"))))
    def main__void():
        atlas = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        p = rt.construct(3, rt.swizzle(atlas, "x"), rt.binary("%", rt.swizzle(atlas, "y"), _u_volumeSize, 1, "int"), rt.binary("/", rt.swizzle(atlas, "y"), _u_volumeSize, 1, "int"), base="int")
        occupied = density__ivec3(p)
        g.fragColor[:] = rt.construct(4, rt.f(0.0))
        g.geoOut[:] = rt.construct(4, rt.f(0.5), rt.f(1.0), rt.f(0.5), rt.f(0.0))
        if rt.binary("==", occupied, rt.f(0.0)):
            return
        color = rt.swizzle(rt.texel_fetch(_u_tex, imageTexel__ivec2_ivec2(rt.swizzle(p, "xz"), rt.texture_size(_u_tex)), rt.i(0)), "rgb")
        g.fragColor[:] = rt.construct(4, color, occupied)
        normal = rt.construct(3, rt.binary("-", density__ivec3(rt.binary("-", p, rt.construct(3, rt.i(1), rt.i(0), rt.i(0), base="int"), 3, "int")), density__ivec3(rt.binary("+", p, rt.construct(3, rt.i(1), rt.i(0), rt.i(0), base="int"), 3, "int")), 1, "float"), rt.binary("-", density__ivec3(rt.binary("-", p, rt.construct(3, rt.i(0), rt.i(1), rt.i(0), base="int"), 3, "int")), density__ivec3(rt.binary("+", p, rt.construct(3, rt.i(0), rt.i(1), rt.i(0), base="int"), 3, "int")), 1, "float"), rt.binary("-", density__ivec3(rt.binary("-", p, rt.construct(3, rt.i(0), rt.i(0), rt.i(1), base="int"), 3, "int")), density__ivec3(rt.binary("+", p, rt.construct(3, rt.i(0), rt.i(0), rt.i(1), base="int"), 3, "int")), 1, "float"))
        normal[:] = (rt.normalize(normal) if rt.binary(">", rt.dot(normal, normal), rt.f(0.0)) else rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)))
        g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), occupied)
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
