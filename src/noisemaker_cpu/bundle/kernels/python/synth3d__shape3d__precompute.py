def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_loopAOffset = U.get("loopAOffset", 0)
    _u_loopBOffset = U.get("loopBOffset", 0)
    _u_loopAScale = U.get("loopAScale", rt.f(0.0))
    _u_loopBScale = U.get("loopBScale", rt.f(0.0))
    _u_speedA = U.get("speedA", rt.f(0.0))
    _u_speedB = U.get("speedB", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def periodicFunction__float(p):
        x = rt.binary("*", g.TAU, p, 1, "float")
        return map__float_float_float_float_float(rt.component_wise("sin", x, width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def tetrahedronSDF__vec3(p):
        p = rt.copy(p, "float")
        s = rt.f(0.5)
        return rt.binary("/", rt.binary("-", rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), width=1), rt.swizzle(p, "z"), 1, "float"), rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), width=1), rt.swizzle(p, "z"), 1, "float"), width=1), s, 1, "float"), rt.component_wise("sqrt", rt.f(3.0), width=1), 1, "float")
    def cubeSDF__vec3(p):
        p = rt.copy(p, "float")
        d = rt.binary("-", rt.component_wise("abs", p, width=3), rt.construct(3, rt.f(0.45)), 3, "float")
        return rt.binary("+", rt.length(rt.component_wise("max", d, rt.f(0.0), width=3)), rt.component_wise("min", rt.component_wise("max", rt.swizzle(d, "x"), rt.component_wise("max", rt.swizzle(d, "y"), rt.swizzle(d, "z"), width=1), width=1), rt.f(0.0), width=1), 1, "float")
    def octahedronSDF__vec3(p):
        p = rt.copy(p, "float")
        p[:] = rt.component_wise("abs", p, width=3)
        s = rt.f(0.5)
        return rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), s, 1, "float"), rt.f(0.57735027), 1, "float")
    def dodecahedronSDF__vec3(p):
        p = rt.copy(p, "float")
        p[:] = rt.component_wise("abs", p, width=3)
        phi = rt.binary("*", rt.binary("+", rt.f(1.0), rt.component_wise("sqrt", rt.f(5.0), width=1), 1, "float"), rt.f(0.5), 1, "float")
        n1 = rt.normalize(rt.construct(3, rt.f(1.0), phi, rt.f(0.0)))
        n2 = rt.normalize(rt.construct(3, rt.f(0.0), rt.f(1.0), phi))
        n3 = rt.normalize(rt.construct(3, phi, rt.f(0.0), rt.f(1.0)))
        d = rt.f(0.0)
        d = rt.component_wise("max", d, rt.dot(p, n1), width=1)
        d = rt.component_wise("max", d, rt.dot(p, n2), width=1)
        d = rt.component_wise("max", d, rt.dot(p, n3), width=1)
        d = rt.component_wise("max", d, rt.swizzle(p, "x"), width=1)
        d = rt.component_wise("max", d, rt.swizzle(p, "y"), width=1)
        d = rt.component_wise("max", d, rt.swizzle(p, "z"), width=1)
        return rt.binary("-", d, rt.f(0.45), 1, "float")
    def icosahedronSDF__vec3(p):
        p = rt.copy(p, "float")
        p[:] = rt.component_wise("abs", p, width=3)
        phi = rt.binary("*", rt.binary("+", rt.f(1.0), rt.component_wise("sqrt", rt.f(5.0), width=1), 1, "float"), rt.f(0.5), 1, "float")
        n1 = rt.normalize(rt.construct(3, phi, rt.f(1.0), rt.f(0.0)))
        n2 = rt.normalize(rt.construct(3, rt.f(1.0), rt.f(0.0), phi))
        n3 = rt.normalize(rt.construct(3, rt.f(0.0), phi, rt.f(1.0)))
        d = rt.f(0.0)
        d = rt.component_wise("max", d, rt.dot(p, n1), width=1)
        d = rt.component_wise("max", d, rt.dot(p, n2), width=1)
        d = rt.component_wise("max", d, rt.dot(p, n3), width=1)
        d = rt.component_wise("max", d, rt.dot(p, rt.normalize(rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(1.0)))), width=1)
        return rt.binary("-", d, rt.f(0.42), 1, "float")
    def sphereSDF__vec3(p):
        p = rt.copy(p, "float")
        return rt.binary("-", rt.length(p), rt.f(0.5), 1, "float")
    def torusSDF__vec3(p):
        p = rt.copy(p, "float")
        t = rt.construct(2, rt.f(0.35), rt.f(0.12))
        q = rt.construct(2, rt.binary("-", rt.length(rt.swizzle(p, "xz")), rt.swizzle(t, "x"), 1, "float"), rt.swizzle(p, "y"))
        return rt.binary("-", rt.length(q), rt.swizzle(t, "y"), 1, "float")
    def cylinderSDF__vec3(p):
        p = rt.copy(p, "float")
        d = rt.binary("-", rt.component_wise("abs", rt.construct(2, rt.length(rt.swizzle(p, "xz")), rt.swizzle(p, "y")), width=2), rt.construct(2, rt.f(0.35), rt.f(0.45)), 2, "float")
        return rt.binary("+", rt.component_wise("min", rt.component_wise("max", rt.swizzle(d, "x"), rt.swizzle(d, "y"), width=1), rt.f(0.0), width=1), rt.length(rt.component_wise("max", d, rt.f(0.0), width=2)), 1, "float")
    def coneSDF__vec3(p):
        p = rt.copy(p, "float")
        h = rt.f(0.6)
        r = rt.f(0.4)
        c = rt.normalize(rt.construct(2, h, r))
        q = rt.length(rt.swizzle(p, "xz"))
        return rt.component_wise("max", rt.dot(rt.swizzle(c, "xy"), rt.construct(2, q, rt.swizzle(p, "y"))), rt.binary("-", rt.unary("-", rt.swizzle(p, "y")), rt.binary("*", h, rt.f(0.5), 1, "float"), 1, "float"), width=1)
    def capsuleSDF__vec3(p):
        p = rt.copy(p, "float")
        h = rt.f(0.3)
        r = rt.f(0.25)
        p = rt.assign_swizzle(p, "y", rt.binary("-", rt.swizzle(p, "y"), rt.component_wise("clamp", rt.swizzle(p, "y"), rt.unary("-", h), h, width=1), 1, "float"))
        return rt.binary("-", rt.length(p), r, 1, "float")
    def shapeSDF__vec3_int(p, shapeType):
        p = rt.copy(p, "float")
        if rt.binary("==", shapeType, rt.i(10)):
            return tetrahedronSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(20)):
            return cubeSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(30)):
            return octahedronSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(40)):
            return dodecahedronSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(50)):
            return icosahedronSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(100)):
            return sphereSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(110)):
            return torusSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(120)):
            return cylinderSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(130)):
            return coneSDF__vec3(p)
        if rt.binary("==", shapeType, rt.i(140)):
            return capsuleSDF__vec3(p)
        return sphereSDF__vec3(p)
    def offset3D__vec3_float_int(p, freq, loopOffset):
        p = rt.copy(p, "float")
        cp = rt.binary("-", p, rt.f(0.5), 3, "float")
        sdf = shapeSDF__vec3_int(cp, loopOffset)
        return rt.binary("*", rt.binary("-", rt.f(0.5), sdf, 1, "float"), freq, 1, "float")
    def computeValue__vec3_float_float(p, lf1, lf2):
        p = rt.copy(p, "float")
        offset1 = offset3D__vec3_float_int(p, lf1, _u_loopAOffset)
        offset2 = offset3D__vec3_float_int(p, lf2, _u_loopBOffset)
        t1 = rt.binary("+", offset1, rt.binary("*", _u_time, rt.component_wise("floor", _u_speedA, width=1), 1, "float"), 1, "float")
        t2 = rt.binary("+", offset2, rt.binary("*", _u_time, rt.component_wise("floor", _u_speedB, width=1), 1, "float"), 1, "float")
        a = periodicFunction__float(t1)
        b = periodicFunction__float(t2)
        return rt.binary("*", rt.binary("+", a, b, 1, "float"), rt.f(0.5), 1, "float")
    def main__void():
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        x = rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="int")
        yAtlas = rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="int")
        y = rt.binary("%", yAtlas, volSize, 1, "int")
        z = rt.binary("/", yAtlas, volSize, 1, "int")
        p = rt.binary("/", rt.construct(3, rt.construct(1, x), rt.construct(1, y), rt.construct(1, z)), rt.binary("-", volSizeF, rt.f(1.0), 1, "float"), 3, "float")
        lf1 = map__float_float_float_float_float(_u_loopAScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        lf2 = map__float_float_float_float_float(_u_loopBScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        d = computeValue__vec3_float_float(p, lf1, lf2)
        eps = rt.binary("/", rt.f(1.0), volSizeF, 1, "float")
        dx = computeValue__vec3_float_float(rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"), lf1, lf2)
        dy = computeValue__vec3_float_float(rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"), lf1, lf2)
        dz = computeValue__vec3_float_float(rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"), lf1, lf2)
        gradient = rt.binary("/", rt.construct(3, rt.binary("-", dx, d, 1, "float"), rt.binary("-", dy, d, 1, "float"), rt.binary("-", dz, d, 1, "float")), eps, 3, "float")
        normal = rt.normalize(rt.binary("+", rt.unary("-", gradient), rt.construct(3, rt.f(1e-06)), 3, "float"))
        g.fragColor[:] = rt.construct(4, d, d, d, rt.f(1.0))
        g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), d)
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
