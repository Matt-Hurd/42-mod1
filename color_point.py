def color_point(color, z):
    green = (7.0 / 255, 175.0 / 255, 43.0 / 255)
    brown = (139.0 / 255, 69.0 / 255, 19.0 / 255)
    white = (255.0 / 255, 255.0 / 255, 255.0 / 255)
    if (z < 0.5):
        p = z / 0.5;
        r = (green[0] * (1.0 - p)) + (brown[0] * p)
        g = (green[1] * (1.0 - p)) + (brown[1] * p)
        b = (green[2] * (1.0 - p)) + (brown[2] * p)
    elif (z <= 1.0):
        p = (z - 0.5) / 0.5;
        r = (brown[0] * (1.0 - p)) + (white[0] * p)
        g = (brown[1] * (1.0 - p)) + (white[1] * p)
        b = (brown[2] * (1.0 - p)) + (white[2] * p)
    else:
        r = 1
        g = 1
        b = 1
    color.addData4f(r, g, b, 1.0)
