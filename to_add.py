import pygame, os
import ctypes


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)

        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        image = image.convert_alpha()
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


class SkinMenu(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('skinMenu.png')
        self.rect = self.image.get_rect()
        self.rect[0] = sizeX - self.rect[2]
        self.rect[1] = sizeY - self.rect[3]
        self.level = 0

class ButtonStart(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('buttonStart.png', -1)
        self.rect = self.image.get_rect()
        self.rect[0] = (sizeX - self.rect[2]) // 2
        self.rect[1] = (sizeY - self.rect[3]) // 2


class Setting(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('setting.png', -1)
        self.rect = self.image.get_rect()
        # self.rect[0] = (sizeX - self.rect[2]) // 2
        self.rect[1] = sizeY - self.rect[3]

pygame.init()
sizeX, sizeY = ctypes.windll.user32.GetSystemMetrics(0) - 100, ctypes.windll.user32.GetSystemMetrics(1) - 100
screen = pygame.display.set_mode((sizeX, sizeY))
level = 0
menu = pygame.sprite.Group()
skinMenu = SkinMenu(menu)
buttonStart = ButtonStart(menu)
setting = Setting(menu)
start = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if not start:
        menu.draw(screen)
    pygame.display.flip()
