from PIL import Image

def do(path, name, reverse):
    im = Image.open("data/" + str(path) + "/parent.jpg")
    pixels = im.load()
    x, y = im.size
    color1, color2 = choose_color(name)
    for i in range(x):
        for j in range(y):
            r, g, b = pixels[i, j]
            if r < 200 or g < 200 or b < 200:
                if not reverse:
                    r, g, b = color1
                    pixels[i, j] = int(r + 3 * ((x / 2 - i) ** 2 + (y / 2 - j) ** 2) ** 0.5), \
                                    int(g + 3 * ((x / 2 - i) ** 2 + (y / 2 - j) ** 2) ** 0.5), \
                                    int(b + 3 * ((x / 2 - i) ** 2 + (y / 2 - j) ** 2) ** 0.5)

                else:
                    r, g, b = color2
                    pixels[i, j] = int(r + 3 * ((x / 2 - i) ** 2 + (y / 2 - j) ** 2) ** 0.5), \
                                    int(g + 3 * ((x / 2 - i) ** 2 + (y / 2 - j) ** 2) ** 0.5), \
                                    int(b + 3 * ((x / 2 - i) ** 2 + (y / 2 - j) ** 2) ** 0.5)
            else:
                pixels[i, j] = 0, 0, 0
    im.save("data/" + str(path) + '/' + name)


def choose_color(name):
    if name == 'aristocrat.png' or name == 'aristocrate.png':
        return (185, 108, 114), (127, 185, 179)
    elif name == 'king.png' or name == 'kinge.png':
        return (182, 181, 107), (129, 69, 105)
    elif name == 'soldier.png' or name == 'soldiere.png':
        return (162, 130, 79), (83, 174, 112)



for i in range(4, 17):
    do(i, 'aristocrat.png', False)
    do(i, 'aristocrate.png', True)
    do(i, 'king.png', False)
    do(i, 'kinge.png', True)
    do(i, 'soldier.png', False)
    do(i, 'soldiere.png', True)
