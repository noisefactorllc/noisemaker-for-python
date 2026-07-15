def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_imageTex = T["imageTex"]
    _u_imageSize = U["imageSize"]
    _u_resolution = U["resolution"]
    _u_time = U["time"]
    _u_position = U["position"]
    _u_rotation = U["rotation"]
    _u_scaleAmt = U["scaleAmt"]
    _u_offsetX = U["offsetX"]
    _u_offsetY = U["offsetY"]
    _u_tiling = U["tiling"]
    _u_flip = U["flip"]
    _u_bgColor = U["bgColor"]
    _u_bgAlpha = U["bgAlpha"]
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st)
        rot = map__float_float_float_float_float(rot, rt.unary("-", rt.f(180.0)), rt.f(180.0), rt.f(0.5), rt.unary("-", rt.f(0.5)))
        angle = rt.binary("*", rt.binary("*", rot, rt.f(6.28318530718), 1, "float"), rt.unary("-", rt.f(1.0)), 1, "float")
        size = _u_imageSize
        aspect = rt.binary("/", rt.swizzle(size, "x"), rt.swizzle(size, "y"), 1, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.f(0.5), aspect, 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st = rt.binary("+", st, rt.construct(2, rt.binary("*", rt.f(0.5), aspect, 1, "float"), rt.f(0.5)), 2, "float")
        return st
    def tile__vec2(st):
        st = rt.copy(st)
        if rt.binary("==", _u_tiling, rt.i(0)):
            return st
        else:
            if rt.binary("==", _u_tiling, rt.i(1)):
                return rt.component_wise("fract", st, width=2)
            else:
                if rt.binary("==", _u_tiling, rt.i(2)):
                    return rt.construct(2, rt.component_wise("fract", rt.swizzle(st, "x"), width=1), rt.swizzle(st, "y"))
                else:
                    if rt.binary("==", _u_tiling, rt.i(3)):
                        return rt.construct(2, rt.swizzle(st, "x"), rt.component_wise("fract", rt.swizzle(st, "y"), width=1))
        return st
    def getImage__vec2(st):
        st = rt.copy(st)
        size = _u_imageSize
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), size, 2, "float")
        st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
        scale = rt.binary("/", rt.f(100.0), _u_scaleAmt, 1, "float")
        if rt.binary("==", scale, rt.f(0.0)):
            scale = rt.f(1.0)
        st = rt.binary("*", st, scale, 2, "float")
        if rt.binary("==", _u_position, rt.i(0)):
            st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.binary("-", scale, rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
        else:
            if rt.binary("==", _u_position, rt.i(1)):
                st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.binary("-", scale, rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
            else:
                if rt.binary("==", _u_position, rt.i(2)):
                    st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                    st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.binary("-", scale, rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                else:
                    if rt.binary("==", _u_position, rt.i(3)):
                        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), scale, 1, "float"), 1, "float"))
                    else:
                        if rt.binary("==", _u_position, rt.i(4)):
                            st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                            st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), scale, 1, "float"), 1, "float"))
                        else:
                            if rt.binary("==", _u_position, rt.i(5)):
                                st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                                st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), scale, 1, "float"), 1, "float"))
                            else:
                                if rt.binary("==", _u_position, rt.i(6)):
                                    st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.f(1.0), rt.binary("-", scale, rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                                else:
                                    if rt.binary("==", _u_position, rt.i(7)):
                                        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                                        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.f(1.0), rt.binary("-", scale, rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                                    else:
                                        if rt.binary("==", _u_position, rt.i(8)):
                                            st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
                                            st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.f(1.0), rt.binary("-", scale, rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("*", map__float_float_float_float_float(_u_offsetX, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.binary("*", rt.binary("/", rt.unary("-", rt.swizzle(_u_resolution, "x")), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float"), rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(size, "x"), 1, "float"), scale, 1, "float")), rt.f(1.5), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "y", rt.binary("-", rt.swizzle(st, "y"), rt.binary("*", map__float_float_float_float_float(_u_offsetY, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.binary("*", rt.binary("/", rt.unary("-", rt.swizzle(_u_resolution, "y")), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float"), rt.binary("*", rt.binary("/", rt.swizzle(_u_resolution, "y"), rt.swizzle(size, "y"), 1, "float"), scale, 1, "float")), rt.f(1.5), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), rt.binary("/", rt.swizzle(size, "x"), rt.swizzle(size, "y"), 1, "float"), 1, "float"))
        st = rotate2D__vec2_float(st, _u_rotation)
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), rt.binary("/", rt.swizzle(size, "x"), rt.swizzle(size, "y"), 1, "float"), 1, "float"))
        st = tile__vec2(st)
        st = rt.binary("+", st, rt.binary("/", rt.f(1.0), size, 2, "float"), 2, "float")
        if rt.binary("==", _u_flip, rt.i(1)):
            st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
            st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
        else:
            if rt.binary("==", _u_flip, rt.i(2)):
                st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
            else:
                if rt.binary("==", _u_flip, rt.i(3)):
                    st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
                else:
                    if rt.binary("==", _u_flip, rt.i(11)):
                        if rt.binary(">", rt.swizzle(st, "x"), rt.f(0.5)):
                            st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
                    else:
                        if rt.binary("==", _u_flip, rt.i(12)):
                            if rt.binary("<", rt.swizzle(st, "x"), rt.f(0.5)):
                                st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
                        else:
                            if rt.binary("==", _u_flip, rt.i(13)):
                                if rt.binary(">", rt.swizzle(st, "y"), rt.f(0.5)):
                                    st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
                            else:
                                if rt.binary("==", _u_flip, rt.i(14)):
                                    if rt.binary("<", rt.swizzle(st, "y"), rt.f(0.5)):
                                        st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
                                else:
                                    if rt.binary("==", _u_flip, rt.i(15)):
                                        if rt.binary(">", rt.swizzle(st, "x"), rt.f(0.5)):
                                            st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
                                        if rt.binary(">", rt.swizzle(st, "y"), rt.f(0.5)):
                                            st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
                                    else:
                                        if rt.binary("==", _u_flip, rt.i(16)):
                                            if rt.binary(">", rt.swizzle(st, "x"), rt.f(0.5)):
                                                st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
                                            if rt.binary("<", rt.swizzle(st, "y"), rt.f(0.5)):
                                                st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
                                        else:
                                            if rt.binary("==", _u_flip, rt.i(17)):
                                                if rt.binary("<", rt.swizzle(st, "x"), rt.f(0.5)):
                                                    st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
                                                if rt.binary(">", rt.swizzle(st, "y"), rt.f(0.5)):
                                                    st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
                                            else:
                                                if rt.binary("==", _u_flip, rt.i(18)):
                                                    if rt.binary("<", rt.swizzle(st, "x"), rt.f(0.5)):
                                                        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.f(1.0), rt.swizzle(st, "x"), 1, "float"))
                                                    if rt.binary("<", rt.swizzle(st, "y"), rt.f(0.5)):
                                                        st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
        text = rt.texture(_u_imageTex, st)
        if (bool((bool((bool(rt.binary("<", rt.swizzle(st, "x"), rt.f(0.0))) or bool(rt.binary(">", rt.swizzle(st, "x"), rt.f(1.0))))) or bool(rt.binary("<", rt.swizzle(st, "y"), rt.f(0.0))))) or bool(rt.binary(">", rt.swizzle(st, "y"), rt.f(1.0)))):
            return rt.construct(4, _u_bgColor, _u_bgAlpha)
        if rt.binary(">", rt.swizzle(text, "a"), rt.f(0.0)):
            text = rt.assign_swizzle(text, "rgb", rt.binary("/", rt.swizzle(text, "rgb"), rt.swizzle(text, "a"), 3, "float"))
        return text
    def main__void():
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        st = rt.assign_swizzle(st, "y", rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float"))
        g.fragColor = getImage__vec2(st)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
