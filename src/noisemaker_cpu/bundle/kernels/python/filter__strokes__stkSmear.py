def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_strokeLength = U.get("strokeLength", rt.f(0.0))
    _u_balance = U.get("balance", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.MAX_TAPS = rt.i(24)
    def hash12__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def valueNoise2__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def hash22__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.construct(3, rt.f(0.1031), rt.f(0.103), rt.f(0.0973)), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "xx"), rt.swizzle(p3, "yz"), 2, "float"), rt.swizzle(p3, "zy"), 2, "float"), width=2)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradient__vec2(uv):
        uv = rt.copy(uv, "float")
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        tl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1, "float"), 1, "float"), br, 1, "float"), tl, 1, "float"), rt.binary("*", rt.f(2.0), l, 1, "float"), 1, "float"), bl, 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), tr, 1, "float"), bl, 1, "float"), rt.binary("*", rt.f(2.0), b, 1, "float"), 1, "float"), br, 1, "float"))
    def rotate2D__vec2_float(v, angleDeg):
        v = rt.copy(v, "float")
        a = rt.component_wise("radians", angleDeg, width=1)
        co = rt.component_wise("cos", a, width=1)
        si = rt.component_wise("sin", a, width=1)
        return rt.matrix_mult(rt.construct(4, co, rt.unary("-", si), si, co), v, 2)
    def strokeVariation__vec2_vec2_float(gc, dirUnit, runBase):
        gc = rt.copy(gc, "float")
        dirUnit = rt.copy(dirUnit, "float")
        across = rt.construct(2, rt.unary("-", rt.swizzle(dirUnit, "y")), rt.swizzle(dirUnit, "x"))
        strokeSpace = rt.construct(2, rt.binary("/", rt.dot(gc, dirUnit), rt.component_wise("max", runBase, rt.f(3.0), width=1), 1, "float"), rt.binary("/", rt.dot(gc, across), rt.f(3.5), 1, "float"))
        return rt.binary("+", rt.f(0.72), rt.binary("*", rt.f(0.56), valueNoise2__vec2(rt.binary("*", strokeSpace, rt.f(0.65), 2, "float")), 1, "float"), 1, "float")
    def brushStrokeField__vec2_vec2_vec2_float(uv, gc, dirUnit, runBase):
        uv = rt.copy(uv, "float")
        gc = rt.copy(gc, "float")
        dirUnit = rt.copy(dirUnit, "float")
        across = rt.construct(2, rt.unary("-", rt.swizzle(dirUnit, "y")), rt.swizzle(dirUnit, "x"))
        oriented = rt.construct(2, rt.dot(gc, dirUnit), rt.dot(gc, across))
        spacing = rt.construct(2, rt.component_wise("max", rt.binary("*", runBase, rt.f(0.7), 1, "float"), rt.f(4.0), width=1), rt.f(4.5))
        baseCell = rt.component_wise("floor", rt.binary("/", oriented, spacing, 2, "float"), width=2)
        field = rt.f(0.0)
        pigmentSum = rt.construct(3, rt.f(0.0))
        pigmentWeight = rt.f(0.0)
        cy = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                cy = rt.binary("+", cy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", cy, rt.i(1))):
                break
            cx = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    cx = rt.binary("+", cx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", cx, rt.i(1))):
                    break
                cell = rt.binary("+", baseCell, rt.construct(2, rt.construct(1, cx), rt.construct(1, cy)), 2, "float")
                jitter = rt.binary("-", hash22__vec2(rt.binary("+", cell, rt.f(17.3), 2, "float")), rt.f(0.5), 2, "float")
                center = rt.binary("*", rt.binary("+", rt.binary("+", cell, rt.f(0.5), 2, "float"), rt.binary("*", jitter, rt.construct(2, rt.f(0.56), rt.f(0.4)), 2, "float"), 2, "float"), spacing, 2, "float")
                delta = rt.binary("-", oriented, center, 2, "float")
                angle = rt.binary("*", rt.binary("-", hash12__vec2(rt.binary("+", cell, rt.f(29.1), 2, "float")), rt.f(0.5), 1, "float"), rt.f(0.34), 1, "float")
                co = rt.component_wise("cos", angle, width=1)
                si = rt.component_wise("sin", angle, width=1)
                local = rt.construct(2, rt.binary("+", rt.binary("*", co, rt.swizzle(delta, "x"), 1, "float"), rt.binary("*", si, rt.swizzle(delta, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.unary("-", si), rt.swizzle(delta, "x"), 1, "float"), rt.binary("*", co, rt.swizzle(delta, "y"), 1, "float"), 1, "float"))
                halfLength = rt.binary("*", runBase, rt.binary("+", rt.f(0.35), rt.binary("*", rt.f(0.18), hash12__vec2(rt.binary("+", cell, rt.f(43.7), 2, "float")), 1, "float"), 1, "float"), 1, "float")
                halfWidth = rt.binary("+", rt.f(1.4), rt.binary("*", rt.f(1.2), hash12__vec2(rt.binary("+", cell, rt.f(71.9), 2, "float")), 1, "float"), 1, "float")
                capsule = rt.binary("-", rt.length(rt.construct(2, rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(local, "x"), width=1), halfLength, 1, "float"), rt.f(0.0), width=1), rt.swizzle(local, "y"))), halfWidth, 1, "float")
                aa = rt.f(1.35)
                body = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.unary("-", aa), aa, capsule, width=1), 1, "float")
                bristle = rt.binary("+", rt.f(0.78), rt.binary("*", rt.f(0.22), rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(local, "y"), rt.f(5.2), 1, "float"), rt.binary("*", hash12__vec2(rt.binary("+", cell, rt.f(97.3), 2, "float")), rt.f(6.2831853), 1, "float"), 1, "float"), width=1), 1, "float"), 1, "float"), 1, "float"), 1, "float")
                mark = rt.binary("*", body, bristle, 1, "float")
                centerGlobal = rt.binary("+", rt.binary("*", dirUnit, rt.swizzle(center, "x"), 2, "float"), rt.binary("*", across, rt.swizzle(center, "y"), 2, "float"), 2, "float")
                centerUV = rt.binary("+", uv, rt.binary("/", rt.binary("-", centerGlobal, gc, 2, "float"), _u_resolution, 2, "float"), 2, "float")
                pigmentSum[:] = rt.binary("+", pigmentSum, rt.binary("*", rt.swizzle(srcSample__vec2(centerUV), "rgb"), mark, 3, "float"), 3, "float")
                pigmentWeight = rt.binary("+", pigmentWeight, mark, 1, "float")
                field = rt.component_wise("max", field, mark, width=1)
        pigment = (rt.binary("/", pigmentSum, pigmentWeight, 3, "float") if rt.binary(">", pigmentWeight, rt.f(0.0001)) else rt.swizzle(srcSample__vec2(uv), "rgb"))
        return rt.construct(4, pigment, rt.component_wise("clamp", field, rt.f(0.0), rt.f(1.0), width=1))
    def sprayJitter__vec2_float(gc, tap):
        gc = rt.copy(gc, "float")
        p = rt.binary("/", gc, rt.f(7.0), 2, "float")
        return rt.binary("-", rt.construct(2, valueNoise2__vec2(rt.binary("+", p, rt.construct(2, rt.binary("*", tap, rt.f(0.73), 1, "float"), rt.f(7.0)), 2, "float")), valueNoise2__vec2(rt.binary("+", rt.binary("+", p, rt.construct(2, rt.f(11.0), rt.binary("*", tap, rt.f(0.79), 1, "float")), 2, "float"), rt.f(37.1), 2, "float"))), rt.f(0.5), 2, "float")
    def srcSample__vec2(sampleUV):
        sampleUV = rt.copy(sampleUV, "float")
        px = rt.construct(2, 0.0)
        s = rt.construct(4, 0.0)
        e = rt.construct(3, 0.0)
        if rt.binary("==", _u_MODE, rt.i(3)):
            px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
            s = rt.texture(_u_inputTex, sampleUV)
            e = rt.swizzle(s, "rgb")
            e[:] = rt.component_wise("min", e, rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", sampleUV, rt.construct(2, rt.swizzle(px, "x"), rt.f(0.0)), 2, "float")), "rgb"), width=3)
            e[:] = rt.component_wise("min", e, rt.swizzle(rt.texture(_u_inputTex, rt.binary("-", sampleUV, rt.construct(2, rt.swizzle(px, "x"), rt.f(0.0)), 2, "float")), "rgb"), width=3)
            e[:] = rt.component_wise("min", e, rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", sampleUV, rt.construct(2, rt.f(0.0), rt.swizzle(px, "y")), 2, "float")), "rgb"), width=3)
            e[:] = rt.component_wise("min", e, rt.swizzle(rt.texture(_u_inputTex, rt.binary("-", sampleUV, rt.construct(2, rt.f(0.0), rt.swizzle(px, "y")), 2, "float")), "rgb"), width=3)
            return rt.construct(4, e, rt.swizzle(s, "a"))
        else:
            return rt.texture(_u_inputTex, sampleUV)
    def smear__vec2_vec2_vec2_float_float(uv, gc, dirUnit, L, jitterPx):
        uv = rt.copy(uv, "float")
        gc = rt.copy(gc, "float")
        dirUnit = rt.copy(dirUnit, "float")
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        sum = srcSample__vec2(uv)
        wsum = rt.f(1.0)
        i = rt.i(1)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<=", i, g.MAX_TAPS)):
                break
            fi = rt.construct(1, i)
            if rt.binary(">", fi, L):
                break
            w = rt.component_wise("exp", rt.binary("/", rt.binary("*", rt.unary("-", rt.f(2.0)), fi, 1, "float"), L, 1, "float"), width=1)
            jp = rt.construct(2, rt.f(0.0))
            jn = rt.construct(2, rt.f(0.0))
            if rt.binary(">", jitterPx, rt.f(0.0)):
                jp[:] = rt.binary("*", sprayJitter__vec2_float(gc, fi), jitterPx, 2, "float")
                jn[:] = rt.binary("*", sprayJitter__vec2_float(rt.binary("+", gc, rt.f(31.7), 2, "float"), rt.unary("-", fi)), jitterPx, 2, "float")
            sampP = rt.binary("+", rt.binary("+", uv, rt.binary("*", rt.binary("*", dirUnit, fi, 2, "float"), px, 2, "float"), 2, "float"), rt.binary("*", jp, px, 2, "float"), 2, "float")
            sampN = rt.binary("+", rt.binary("-", uv, rt.binary("*", rt.binary("*", dirUnit, fi, 2, "float"), px, 2, "float"), 2, "float"), rt.binary("*", jn, px, 2, "float"), 2, "float")
            sum[:] = rt.binary("+", sum, rt.binary("*", rt.binary("+", srcSample__vec2(sampP), srcSample__vec2(sampN), 4, "float"), w, 4, "float"), 4, "float")
            wsum = rt.binary("+", wsum, rt.binary("*", rt.f(2.0), w, 1, "float"), 1, "float")
        return rt.binary("/", sum, wsum, 4, "float")
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        gc = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        runBase = rt.component_wise("mix", rt.f(3.0), rt.f(50.0), rt.binary("/", _u_strokeLength, rt.f(100.0), 1, "float"), width=1)
        outc = rt.construct(4, 0.0)
        dir45 = rt.construct(2, 0.0)
        dir135 = rt.construct(2, 0.0)
        l45 = rt.f(0.0)
        l135 = rt.f(0.0)
        layer45 = rt.construct(4, 0.0)
        layer135 = rt.construct(4, 0.0)
        pigment45 = rt.construct(4, 0.0)
        pigment135 = rt.construct(4, 0.0)
        field45 = rt.construct(4, 0.0)
        field135 = rt.construct(4, 0.0)
        b = rt.f(0.0)
        side = rt.f(0.0)
        L = rt.f(0.0)
        jitterPx = rt.f(0.0)
        layer = rt.construct(4, 0.0)
        pigment = rt.construct(4, 0.0)
        c = rt.construct(4, 0.0)
        t = rt.f(0.0)
        bAmt = rt.f(0.0)
        exponent = rt.f(0.0)
        grad = rt.construct(2, 0.0)
        gradMag = rt.f(0.0)
        edgeAngle = rt.f(0.0)
        dir = rt.construct(2, 0.0)
        smeared = rt.construct(4, 0.0)
        shadowMask = rt.f(0.0)
        if rt.binary("==", _u_MODE, rt.i(0)):
            dir45 = rotate2D__vec2_float(rt.construct(2, rt.f(1.0), rt.f(0.0)), rt.f(45.0))
            dir135 = rotate2D__vec2_float(rt.construct(2, rt.f(1.0), rt.f(0.0)), rt.f(135.0))
            l45 = rt.binary("*", runBase, strokeVariation__vec2_vec2_float(gc, dir45, runBase), 1, "float")
            l135 = rt.binary("*", runBase, strokeVariation__vec2_vec2_float(gc, dir135, runBase), 1, "float")
            layer45 = brushStrokeField__vec2_vec2_vec2_float(uv, gc, dir45, runBase)
            layer135 = brushStrokeField__vec2_vec2_vec2_float(uv, gc, dir135, runBase)
            pigment45 = rt.component_wise("mix", smear__vec2_vec2_vec2_float_float(uv, gc, dir45, l45, rt.f(0.0)), rt.construct(4, rt.swizzle(layer45, "rgb"), rt.swizzle(src, "a")), rt.f(0.72), width=4)
            pigment135 = rt.component_wise("mix", smear__vec2_vec2_vec2_float_float(uv, gc, dir135, l135, rt.f(0.0)), rt.construct(4, rt.swizzle(layer135, "rgb"), rt.swizzle(src, "a")), rt.f(0.72), width=4)
            field45 = rt.component_wise("mix", src, pigment45, rt.swizzle(layer45, "a"), width=4)
            field135 = rt.component_wise("mix", src, pigment135, rt.swizzle(layer135, "a"), width=4)
            b = rt.binary("/", _u_balance, rt.f(100.0), 1, "float")
            side = rt.component_wise("smoothstep", rt.binary("-", b, rt.f(0.1), 1, "float"), rt.binary("+", b, rt.f(0.1), 1, "float"), lum__vec3(rt.swizzle(src, "rgb")), width=1)
            outc[:] = rt.component_wise("mix", field135, field45, side, width=4)
        else:
            if rt.binary("==", _u_MODE, rt.i(1)):
                dir45 = rotate2D__vec2_float(rt.construct(2, rt.f(1.0), rt.f(0.0)), rt.f(45.0))
                L = rt.binary("*", runBase, strokeVariation__vec2_vec2_float(gc, dir45, runBase), 1, "float")
                jitterPx = rt.binary("*", rt.binary("/", _u_intensity, rt.f(100.0), 1, "float"), rt.f(6.0), 1, "float")
                layer = brushStrokeField__vec2_vec2_vec2_float(uv, gc, dir45, runBase)
                pigment = rt.component_wise("mix", smear__vec2_vec2_vec2_float_float(uv, gc, dir45, L, jitterPx), rt.construct(4, rt.swizzle(layer, "rgb"), rt.swizzle(src, "a")), rt.f(0.68), width=4)
                outc[:] = rt.component_wise("mix", src, pigment, rt.swizzle(layer, "a"), width=4)
            else:
                if rt.binary("==", _u_MODE, rt.i(2)):
                    dir45 = rotate2D__vec2_float(rt.construct(2, rt.f(1.0), rt.f(0.0)), rt.f(45.0))
                    L = rt.binary("*", runBase, strokeVariation__vec2_vec2_float(gc, dir45, runBase), 1, "float")
                    layer = brushStrokeField__vec2_vec2_vec2_float(uv, gc, dir45, runBase)
                    pigment = rt.component_wise("mix", smear__vec2_vec2_vec2_float_float(uv, gc, dir45, L, rt.f(0.0)), rt.construct(4, rt.swizzle(layer, "rgb"), rt.swizzle(src, "a")), rt.f(0.72), width=4)
                    c = rt.component_wise("mix", src, pigment, rt.swizzle(layer, "a"), width=4)
                    t = lum__vec3(rt.swizzle(c, "rgb"))
                    bAmt = rt.binary("/", _u_balance, rt.f(100.0), 1, "float")
                    exponent = (rt.binary("+", rt.f(1.0), rt.binary("/", _u_intensity, rt.f(50.0), 1, "float"), 1, "float") if rt.binary("<", t, bAmt) else rt.binary("/", rt.f(1.0), rt.binary("+", rt.f(1.0), rt.binary("/", _u_intensity, rt.f(100.0), 1, "float"), 1, "float"), 1, "float"))
                    c = rt.assign_swizzle(c, "rgb", rt.component_wise("pow", rt.component_wise("max", rt.swizzle(c, "rgb"), rt.construct(3, rt.f(0.0)), width=3), rt.construct(3, exponent), width=3))
                    outc[:] = c
                else:
                    if rt.binary("==", _u_MODE, rt.i(3)):
                        dir135 = rotate2D__vec2_float(rt.construct(2, rt.f(1.0), rt.f(0.0)), rt.f(135.0))
                        L = rt.binary("*", runBase, strokeVariation__vec2_vec2_float(gc, dir135, runBase), 1, "float")
                        layer = brushStrokeField__vec2_vec2_vec2_float(uv, gc, dir135, runBase)
                        pigment = rt.component_wise("mix", smear__vec2_vec2_vec2_float_float(uv, gc, dir135, L, rt.f(0.0)), rt.construct(4, rt.swizzle(layer, "rgb"), rt.swizzle(src, "a")), rt.f(0.74), width=4)
                        c = rt.component_wise("mix", src, pigment, rt.swizzle(layer, "a"), width=4)
                        c = rt.assign_swizzle(c, "rgb", rt.component_wise("pow", rt.component_wise("max", rt.swizzle(c, "rgb"), rt.construct(3, rt.f(0.0)), width=3), rt.construct(3, rt.binary("+", rt.f(1.0), rt.binary("/", _u_intensity, rt.f(50.0), 1, "float"), 1, "float")), width=3))
                        outc[:] = c
                    else:
                        grad = lumGradient__vec2(uv)
                        gradMag = rt.length(grad)
                        edgeAngle = (rt.binary("+", rt.component_wise("degrees", rt.component_wise("atan", rt.swizzle(grad, "y"), rt.swizzle(grad, "x"), width=1), width=1), rt.f(90.0), 1, "float") if rt.binary(">", gradMag, rt.f(1e-05)) else rt.f(45.0))
                        dir = rotate2D__vec2_float(rt.construct(2, rt.f(1.0), rt.f(0.0)), edgeAngle)
                        L = rt.binary("*", runBase, strokeVariation__vec2_vec2_float(gc, dir, runBase), 1, "float")
                        layer = brushStrokeField__vec2_vec2_vec2_float(uv, gc, dir, runBase)
                        pigment = rt.component_wise("mix", smear__vec2_vec2_vec2_float_float(uv, gc, dir, L, rt.f(0.0)), rt.construct(4, rt.swizzle(layer, "rgb"), rt.swizzle(src, "a")), rt.f(0.64), width=4)
                        smeared = rt.component_wise("mix", src, pigment, rt.swizzle(layer, "a"), width=4)
                        shadowMask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.55), rt.f(0.65), lum__vec3(rt.swizzle(src, "rgb")), width=1), 1, "float")
                        outc[:] = rt.component_wise("mix", src, smeared, shadowMask, width=4)
        g.fragColor[:] = rt.construct(4, rt.component_wise("clamp", rt.swizzle(outc, "rgb"), rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
