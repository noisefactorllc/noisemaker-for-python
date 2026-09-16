def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_VIEW_MODE = U.get("VIEW_MODE", 0)
    _u_volumeCache = T["volumeCache"]
    _u_analyticalGeo = T["analyticalGeo"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_zoom = U.get("zoom", rt.f(0.0))
    _u_panX = U.get("panX", rt.f(0.0))
    _u_panY = U.get("panY", rt.f(0.0))
    _u_lightDirection = U.get("lightDirection", rt.construct(3, 0.0))
    _u_ambient = U.get("ambient", rt.f(0.0))
    _u_diffuseIntensity = U.get("diffuseIntensity", rt.f(0.0))
    _u_specularIntensity = U.get("specularIntensity", rt.f(0.0))
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    _u_bgAlpha = U.get("bgAlpha", rt.f(0.0))
    _u_rotateX = U.get("rotateX", rt.f(0.0))
    _u_rotateY = U.get("rotateY", rt.f(0.0))
    _u_rotateZ = U.get("rotateZ", rt.f(0.0))
    _u_viewScale = U.get("viewScale", rt.f(0.0))
    _u_posX = U.get("posX", rt.f(0.0))
    _u_posY = U.get("posY", rt.f(0.0))
    _u_posZ = U.get("posZ", rt.f(0.0))
    _u_fieldOfView = U.get("fieldOfView", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    def lighting__vec3_vec3_vec3(color, normal, viewDirection):
        color = rt.copy(color, "float")
        normal = rt.copy(normal, "float")
        viewDirection = rt.copy(viewDirection, "float")
        light = rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0))
        if rt.binary(">", rt.dot(_u_lightDirection, _u_lightDirection), rt.f(1e-06)):
            light[:] = rt.normalize(_u_lightDirection)
        halfVector = rt.binary("+", light, viewDirection, 3, "float")
        specular = rt.f(0.0)
        if rt.binary(">", rt.dot(halfVector, halfVector), rt.f(1e-06)):
            specular = rt.binary("*", rt.component_wise("pow", rt.component_wise("max", rt.dot(normal, rt.normalize(halfVector)), rt.f(0.0), width=1), rt.f(32.0), width=1), _u_specularIntensity, 1, "float")
        return rt.binary("+", rt.binary("*", color, rt.binary("+", _u_ambient, rt.binary("*", rt.component_wise("max", rt.dot(normal, light), rt.f(0.0), width=1), _u_diffuseIntensity, 1, "float"), 1, "float"), 3, "float"), specular, 3, "float")
    def inverseRotation__vec3(p):
        p = rt.copy(p, "float")
        c = rt.component_wise("cos", rt.construct(3, _u_rotateX, _u_rotateY, _u_rotateZ), width=3)
        s = rt.component_wise("sin", rt.construct(3, _u_rotateX, _u_rotateY, _u_rotateZ), width=3)
        p[:] = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(c, "z"), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(s, "z"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.swizzle(s, "z"), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(c, "z"), 1, "float"), 1, "float"), rt.swizzle(p, "z"))
        p[:] = rt.construct(3, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(c, "y"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(s, "y"), 1, "float"), 1, "float"), rt.swizzle(p, "y"), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(s, "y"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(c, "y"), 1, "float"), 1, "float"))
        return rt.construct(3, rt.swizzle(p, "x"), rt.binary("+", rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(c, "x"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(s, "x"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.swizzle(s, "x"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(c, "x"), 1, "float"), 1, "float"))
    def forwardRotation__vec3(p):
        p = rt.copy(p, "float")
        c = rt.component_wise("cos", rt.construct(3, _u_rotateX, _u_rotateY, _u_rotateZ), width=3)
        s = rt.component_wise("sin", rt.construct(3, _u_rotateX, _u_rotateY, _u_rotateZ), width=3)
        p[:] = rt.construct(3, rt.swizzle(p, "x"), rt.binary("-", rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(c, "x"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(s, "x"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(s, "x"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(c, "x"), 1, "float"), 1, "float"))
        p[:] = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(c, "y"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(s, "y"), 1, "float"), 1, "float"), rt.swizzle(p, "y"), rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.swizzle(s, "y"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(c, "y"), 1, "float"), 1, "float"))
        return rt.construct(3, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(c, "z"), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(s, "z"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(s, "z"), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(c, "z"), 1, "float"), 1, "float"), rt.swizzle(p, "z"))
    def renderPerspective__vec2(uv):
        uv = rt.copy(uv, "float")
        size = rt.construct(1, _u_volumeSize)
        focalLength = rt.binary("/", rt.f(1.0), rt.component_wise("tan", rt.binary("*", rt.component_wise("clamp", _u_fieldOfView, rt.f(10.0), rt.f(150.0), width=1), rt.f(0.00872664626), 1, "float"), width=1), 1, "float")
        origin = rt.binary("*", rt.binary("+", rt.binary("/", inverseRotation__vec3(rt.construct(3, rt.unary("-", _u_posX), rt.unary("-", _u_posY), rt.binary("-", rt.f(80.0), _u_posZ, 1, "float"))), rt.f(80.0), 3, "float"), rt.f(0.5), 3, "float"), size, 3, "float")
        framedUv = rt.binary("/", rt.binary("+", uv, rt.construct(2, _u_panX, _u_panY), 2, "float"), rt.component_wise("max", _u_zoom, rt.f(0.001), width=1), 2, "float")
        cameraRay = rt.construct(3, rt.binary("/", rt.binary("*", framedUv, rt.f(2.0), 2, "float"), rt.binary("*", focalLength, rt.component_wise("max", _u_viewScale, rt.f(0.001), width=1), 1, "float"), 2, "float"), rt.unary("-", rt.f(1.0)))
        direction = rt.binary("*", inverseRotation__vec3(cameraRay), rt.binary("/", size, rt.f(80.0), 1, "float"), 3, "float")
        nearT = rt.construct(3, rt.unary("-", rt.f(1e+30)))
        farT = rt.construct(3, rt.f(1e+30))
        delta = rt.construct(3, rt.f(1e+30))
        stepDir = rt.construct(3, rt.i(0), base="int")
        axis = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                axis = rt.binary("+", axis, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", axis, rt.i(3))):
                break
            a = rt.f(0.0)
            b = rt.f(0.0)
            if rt.binary("<", rt.component_wise("abs", direction[int(axis)], width=1), rt.f(1e-08)):
                if (bool(rt.binary("<", origin[int(axis)], rt.f(0.0))) or bool(rt.binary(">=", origin[int(axis)], size))):
                    return
            else:
                a = rt.binary("/", rt.unary("-", origin[int(axis)]), direction[int(axis)], 1, "float")
                b = rt.binary("/", rt.binary("-", size, origin[int(axis)], 1, "float"), direction[int(axis)], 1, "float")
                nearT[int(axis)] = rt.component_wise("min", a, b, width=1)
                farT[int(axis)] = rt.component_wise("max", a, b, width=1)
                delta[int(axis)] = rt.binary("/", rt.f(1.0), rt.component_wise("abs", direction[int(axis)], width=1), 1, "float")
                stepDir[int(axis)] = (rt.i(1) if rt.binary(">", direction[int(axis)], rt.f(0.0)) else rt.unary("-", rt.i(1)))
        enter = rt.component_wise("max", rt.component_wise("max", rt.swizzle(nearT, "x"), rt.swizzle(nearT, "y"), width=1), rt.swizzle(nearT, "z"), width=1)
        leave = rt.component_wise("min", rt.component_wise("min", rt.swizzle(farT, "x"), rt.swizzle(farT, "y"), width=1), rt.swizzle(farT, "z"), width=1)
        distance = rt.component_wise("max", enter, rt.f(0.1), width=1)
        if rt.binary(">=", distance, leave):
            return
        cell = rt.component_wise("clamp", rt.construct(3, rt.component_wise("floor", rt.binary("+", rt.binary("+", origin, rt.binary("*", direction, distance, 3, "float"), 3, "float"), rt.binary("*", rt.construct(3, stepDir), rt.f(0.0001), 3, "float"), 3, "float"), width=3), base="int"), rt.construct(3, rt.i(0), base="int"), rt.construct(3, rt.binary("-", _u_volumeSize, rt.i(1), 1, "int"), base="int"), width=3)
        nextT = rt.construct(3, rt.f(1e+30))
        axis = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                axis = rt.binary("+", axis, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", axis, rt.i(3))):
                break
            boundary = rt.f(0.0)
            if rt.binary("!=", stepDir[int(axis)], rt.i(0)):
                boundary = rt.binary("+", rt.construct(1, cell[int(axis)]), (rt.f(1.0) if rt.binary(">", stepDir[int(axis)], rt.i(0)) else rt.f(0.0)), 1, "float")
                nextT[int(axis)] = rt.binary("/", rt.binary("-", boundary, origin[int(axis)], 1, "float"), direction[int(axis)], 1, "float")
        viewDirection = rt.normalize(rt.unary("-", cameraRay))
        normal = rt.normalize(rt.unary("-", direction))
        if rt.binary(">=", enter, rt.f(0.1)):
            normal[:] = rt.construct(3, rt.f(0.0))
            if (bool(rt.binary(">=", rt.swizzle(nearT, "y"), rt.swizzle(nearT, "x"))) and bool(rt.binary(">=", rt.swizzle(nearT, "y"), rt.swizzle(nearT, "z")))):
                normal = rt.assign_swizzle(normal, "y", rt.unary("-", rt.construct(1, rt.swizzle(stepDir, "y"))))
            else:
                if rt.binary(">=", rt.swizzle(nearT, "x"), rt.swizzle(nearT, "z")):
                    normal = rt.assign_swizzle(normal, "x", rt.unary("-", rt.construct(1, rt.swizzle(stepDir, "x"))))
                else:
                    normal = rt.assign_swizzle(normal, "z", rt.unary("-", rt.construct(1, rt.swizzle(stepDir, "z"))))
        step = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                step = rt.binary("+", step, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<", step, rt.binary("*", _u_volumeSize, rt.i(3), 1, "int"))):
                break
            if (bool((bool(rt.component_wise("any", rt.component_wise("lessThan", cell, rt.construct(3, rt.i(0), base="int"), width=3), width=3)) or bool(rt.component_wise("any", rt.component_wise("greaterThanEqual", cell, rt.construct(3, _u_volumeSize, base="int"), width=3), width=3)))) or bool(rt.binary(">=", distance, leave))):
                break
            atlas = rt.construct(2, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.binary("*", rt.swizzle(cell, "z"), _u_volumeSize, 1, "int"), 1, "int"), base="int")
            density = rt.swizzle(rt.texel_fetch(_u_analyticalGeo, atlas, rt.i(0)), "a")
            worldNormal = rt.construct(3, 0.0)
            if (bool(rt.binary(">", density, rt.f(0.0))) and bool(rt.binary(">=", density, _u_threshold))):
                worldNormal = forwardRotation__vec3(normal)
                g.fragColor[:] = rt.construct(4, lighting__vec3_vec3_vec3(rt.swizzle(rt.texel_fetch(_u_volumeCache, atlas, rt.i(0)), "rgb"), worldNormal, viewDirection), rt.f(1.0))
                g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", worldNormal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), rt.component_wise("clamp", rt.binary("/", distance, rt.f(320.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1))
                return
            distance = rt.component_wise("min", rt.component_wise("min", rt.swizzle(nextT, "x"), rt.swizzle(nextT, "y"), width=1), rt.swizzle(nextT, "z"), width=1)
            crossed = rt.component_wise("lessThanEqual", nextT, rt.construct(3, distance), width=3)
            normal[:] = rt.construct(3, rt.f(0.0))
            if rt.swizzle(crossed, "y"):
                normal = rt.assign_swizzle(normal, "y", rt.unary("-", rt.construct(1, rt.swizzle(stepDir, "y"))))
            else:
                if rt.swizzle(crossed, "x"):
                    normal = rt.assign_swizzle(normal, "x", rt.unary("-", rt.construct(1, rt.swizzle(stepDir, "x"))))
                else:
                    normal = rt.assign_swizzle(normal, "z", rt.unary("-", rt.construct(1, rt.swizzle(stepDir, "z"))))
            cell[:] = rt.binary("+", cell, rt.binary("*", rt.construct(3, crossed, base="int"), stepDir, 3, "int"), 3, "int")
            nextT[:] = rt.binary("+", nextT, rt.binary("*", rt.construct(3, crossed), delta, 3, "float"), 3, "float")
    def main__void():
        g.fragColor[:] = rt.construct(4, rt.binary("*", _u_bgColor, _u_bgAlpha, 3, "float"), _u_bgAlpha)
        g.geoOut[:] = rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(1.0), rt.f(1.0))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        uv = rt.binary("/", rt.binary("-", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), rt.binary("*", fullRes, rt.f(0.5), 2, "float"), 2, "float"), rt.swizzle(fullRes, "y"), 2, "float")
        size = rt.f(0.0)
        aspect = rt.f(0.0)
        span = rt.f(0.0)
        right = rt.construct(3, 0.0)
        up = rt.construct(3, 0.0)
        origin = rt.construct(3, 0.0)
        nearT = rt.construct(3, 0.0)
        enter = rt.f(0.0)
        leave = rt.f(0.0)
        distance = rt.f(0.0)
        cell = rt.construct(3, 0.0, base="int")
        nextT = rt.construct(3, 0.0)
        normal = rt.construct(3, 0.0)
        if rt.binary("==", _u_VIEW_MODE, rt.i(2)):
            renderPerspective__vec2(uv)
        else:
            size = rt.construct(1, _u_volumeSize)
            aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
            span = rt.binary("/", rt.binary("*", rt.binary("*", rt.component_wise("max", rt.f(1.6329931619), rt.binary("/", rt.f(1.4142135624), aspect, 1, "float"), width=1), size, 1, "float"), rt.f(1.08), 1, "float"), rt.component_wise("max", _u_zoom, rt.f(0.001), width=1), 1, "float")
            right = rt.construct(3, rt.f(0.7071067812), rt.f(0.0), rt.unary("-", rt.f(0.7071067812)))
            up = rt.construct(3, rt.unary("-", rt.f(0.4082482905)), rt.f(0.8164965809), rt.unary("-", rt.f(0.4082482905)))
            origin = rt.binary("+", rt.binary("+", rt.construct(3, rt.binary("*", size, rt.f(2.5), 1, "float")), rt.binary("*", rt.binary("*", right, rt.binary("+", rt.swizzle(uv, "x"), _u_panX, 1, "float"), 3, "float"), span, 3, "float"), 3, "float"), rt.binary("*", rt.binary("*", up, rt.binary("+", rt.swizzle(uv, "y"), _u_panY, 1, "float"), 3, "float"), span, 3, "float"), 3, "float")
            nearT = rt.binary("-", origin, size, 3, "float")
            enter = rt.component_wise("max", rt.component_wise("max", rt.swizzle(nearT, "x"), rt.swizzle(nearT, "y"), width=1), rt.swizzle(nearT, "z"), width=1)
            leave = rt.component_wise("min", rt.component_wise("min", rt.swizzle(origin, "x"), rt.swizzle(origin, "y"), width=1), rt.swizzle(origin, "z"), width=1)
            if rt.binary(">=", enter, leave):
                return
            distance = rt.component_wise("max", enter, rt.f(0.0), width=1)
            cell = rt.component_wise("clamp", rt.construct(3, rt.component_wise("floor", rt.binary("-", origin, rt.binary("+", distance, rt.f(0.0001), 1, "float"), 3, "float"), width=3), base="int"), rt.construct(3, rt.i(0), base="int"), rt.construct(3, rt.binary("-", _u_volumeSize, rt.i(1), 1, "int"), base="int"), width=3)
            nextT = rt.binary("-", origin, rt.construct(3, cell), 3, "float")
            normal = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0))
            if (bool(rt.binary(">=", rt.swizzle(nearT, "y"), rt.swizzle(nearT, "x"))) and bool(rt.binary(">=", rt.swizzle(nearT, "y"), rt.swizzle(nearT, "z")))):
                (normal.__setitem__(0, rt.f(0.0)), normal.__setitem__(1, rt.f(1.0)), normal.__setitem__(2, rt.f(0.0)), normal)[-1]
            else:
                if rt.binary(">=", rt.swizzle(nearT, "x"), rt.swizzle(nearT, "z")):
                    (normal.__setitem__(0, rt.f(1.0)), normal.__setitem__(1, rt.f(0.0)), normal.__setitem__(2, rt.f(0.0)), normal)[-1]
            step = rt.i(0)
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    step = rt.binary("+", step, rt.i(1), 1, "int")
                _for3_first = False
                if not (rt.binary("<", step, rt.binary("*", _u_volumeSize, rt.i(3), 1, "int"))):
                    break
                if (bool(rt.component_wise("any", rt.component_wise("lessThan", cell, rt.construct(3, rt.i(0), base="int"), width=3), width=3)) or bool(rt.binary(">=", distance, leave))):
                    break
                atlas = rt.construct(2, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.binary("*", rt.swizzle(cell, "z"), _u_volumeSize, 1, "int"), 1, "int"), base="int")
                density = rt.swizzle(rt.texel_fetch(_u_analyticalGeo, atlas, rt.i(0)), "a")
                color = rt.construct(3, 0.0)
                if (bool(rt.binary(">", density, rt.f(0.0))) and bool(rt.binary(">=", density, _u_threshold))):
                    color = rt.swizzle(rt.texel_fetch(_u_volumeCache, atlas, rt.i(0)), "rgb")
                    g.fragColor[:] = rt.construct(4, lighting__vec3_vec3_vec3(color, normal, rt.construct(3, rt.f(0.5773502692))), rt.f(1.0))
                    g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), rt.component_wise("clamp", rt.binary("/", distance, rt.binary("*", size, rt.f(4.0), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1))
                    return
                distance = rt.component_wise("min", rt.component_wise("min", rt.swizzle(nextT, "x"), rt.swizzle(nextT, "y"), width=1), rt.swizzle(nextT, "z"), width=1)
                crossed = rt.component_wise("lessThanEqual", nextT, rt.construct(3, distance), width=3)
                if rt.swizzle(crossed, "y"):
                    (normal.__setitem__(0, rt.f(0.0)), normal.__setitem__(1, rt.f(1.0)), normal.__setitem__(2, rt.f(0.0)), normal)[-1]
                else:
                    if rt.swizzle(crossed, "x"):
                        (normal.__setitem__(0, rt.f(1.0)), normal.__setitem__(1, rt.f(0.0)), normal.__setitem__(2, rt.f(0.0)), normal)[-1]
                    else:
                        (normal.__setitem__(0, rt.f(0.0)), normal.__setitem__(1, rt.f(0.0)), normal.__setitem__(2, rt.f(1.0)), normal)[-1]
                cell[:] = rt.binary("-", cell, rt.construct(3, crossed, base="int"), 3, "int")
                nextT[:] = rt.binary("+", nextT, rt.construct(3, crossed), 3, "float")
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
