def RGBtoYUV(R, G, B):
    Y = (66 * R + 129 * G + 25 * B + 128) >> 8 + 16
    U = (-38 * R - 74 - G + 112 * B + 128) >> 8 + 128
    V = (112 * R - 94 * G - 18 * B + 128) >> 8 + 128
    return (Y, U, V)


def clip(x):
    if x > 255:
        return 255
    if x < 0:
        return 0
    return x


def YUVtoRGB(Y, U, V):
    C = Y - 16
    D = U - 128
    E = V - 128
    R = clip((298 * C + 409 * E + 128) >> 8)
    G = clip((298 * C - 100 * D - 208 * E + 128) >> 8)
    B = clip((298 * C + 516 * D + 128) >> 8)
    return (R, G, B)