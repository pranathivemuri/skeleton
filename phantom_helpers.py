import numpy as np
import cv2


def createVesselTree(addNoise=False):
    """
    create a simple tree of vessels inside of 512 cube
    MJP 2016.06.10
    This graph looks rather bad, but it works.
    Currently has two unconnected sets of branching tubes
    """
    cubeEdge = 512
    stack = np.ones((cubeEdge, cubeEdge, cubeEdge)) * 20

    p1, p2 = (0, 5, 15), (cubeEdge, 480, 400)
    radius = 35
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (160, 154, 138), (400, 94, 380)
    radius = 20
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (292, 122, 270), (500, 250, 400)
    radius = 15
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (241, 243, 185), (475, 424, 190)
    radius = 12
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (368, 359, 311), (200, 208, 303)
    radius = 12
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (345, 318, 280), (510, 322, 459)
    radius = 18
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (cubeEdge, 105, 91), (0, 446, 200)
    radius = 15
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (86, 380, 50), (35, 30, cubeEdge)
    radius = 20
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (325, 69, 158), (cubeEdge, 230, 100)
    radius = 15
    stack = createCylinder(stack, p1, p2, radius)
    if addNoise:
        stack = _blurVessels(stack, sigma=9)
        stack = _addNoise(stack, level=30, sigma=3)
    return np.amax(stack.astype(bool), 0)


def createOneLargeVesselInclined(radius=35):
    cubeEdge = 512
    stack = np.ones((cubeEdge, cubeEdge, cubeEdge)) * 20
    p1, p2 = (0, 5, 15), (cubeEdge, 480, 400)
    stack = createCylinder(stack, p1, p2, radius)
    return np.amax(stack.astype(bool), 0)


def createOneSmallVesselInclined(radius=20):
    cubeEdge = 512
    stack = np.ones((cubeEdge, cubeEdge, cubeEdge)) * 20
    p1, p2 = (160, 154, 138), (400, 94, 380)
    stack = createCylinder(stack, p1, p2, radius)
    return np.amax(stack.astype(bool), 0)


def createVesselLoop(addNoise=False):
    """
    create a simple tree of vessels inside of 512 cube
    """
    cubeEdge = 512
    stack = np.ones((cubeEdge, cubeEdge, cubeEdge)) * 20

    p1, p2 = (1, 5, 15), (cubeEdge, 480, 400)
    radius = 35
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (154, 138, 160), (94, 380, 400)
    radius = 20
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (122, 258, 282), (254, 454, 459)
    radius = 17
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (280, 276, 470), (325, 276, 40)
    radius = 17
    stack = createCylinder(stack, p1, p2, radius)

    p1, p2 = (234, 419, 429), (319, 272, 108)
    radius = 17
    stack = createCylinder(stack, p1, p2, radius)
    if addNoise:
        stack = _blurVessels(stack, sigma=9)
        stack = _addNoise(stack, level=30, sigma=3)
    return np.amax(stack.astype(bool), 0)


def createCylinder(stack, p1, p2, r):
    """
    given two tuples with the start and end points, create a cylinder between these points with radius r
    This method modifies stack in place, but still returns the stack.
    This is a sloppy way to create a cylinder but it will work for now
    """
    # line goes through point (x0, y0, z0) and in direction of unit vector (u1, u2, u3)
    # point on line closest to (x, y, z) is
    # (X0,Y0,Z0) + ((X-X0)u1+(Y-Y0)u2+(Z-Z0)u3) (u1,u2,u3)

    # (x-x0)^2 + (y-y0)^2 = r^2
    if p1[0] > p2[0]:  # points need to have the first point have a lower Z
        p1, p2 = p2, p1  # swap
    z = np.arange(p1[0], p2[0])
    n = len(z)
    x, y = np.linspace(p1[1], p2[1], n, dtype=int), np.linspace(p1[2], p2[2], n, dtype=int)
    color = 255  # white
    thickness = -1  # filled circle
    for i, zz in enumerate(z):
        stack[zz, :, :] = cv2.circle(stack[zz, :, :].copy(), (x[i], y[i]), r, color, thickness)
    return stack


def _blurVessels(stack, sigma=20):
    """
    smooth out the edges of the vessels
    """
    assert sigma % 2 == 1, "only odd kernel sizes are allowed"
    for i in range(stack.shape[2]):
        stack[i, :, :] = cv2.GaussianBlur(stack[i, :, :].copy(), (sigma, sigma), 0)
    return stack


def _addNoise(stack, level=10, sigma=3):
    """
    add noise defined by level (+- value, within 255) and sigma (std of gaussian kernel)
    """
    assert sigma % 2 == 1, "only odd kernel sizes are allowed"
    noise = np.random.random_integers(-level, level, stack.shape).astype(np.float64)
    for i in range(noise.shape[2]):
        noise[i, :, :] = cv2.GaussianBlur(noise[i, :, :].copy(), (sigma, sigma), 0)
    stack += noise
    # add another level of speckle, just because it's actually this hard
    noise2 = np.random.random_integers(-level, level, stack.shape).astype(np.float64)
    stack += noise2
    stack = stack.clip(0, 255)
    return stack
