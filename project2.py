import pygame, os, random


def write(position, text):
    font = pygame.font.SysFont('Times New Roman', 20)
    text = font.render(text, 1, (255, 255, 255))
    screen.blit(text, position)



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


class Figure(pygame.sprite.Sprite):
    def __init__(self, group, pos, image, velocity, mass):
        super().__init__(group)
        self.mass = mass
        self.velocity = velocity
        self.opposition = player if group is evil else evil
        self.image = image
        self.rect = self.image.get_rect()
        self.rect[:2] = pos
        self.new_coords = pos
        self.attack = []
        self.radius = -1

    def set_image(self, image):
        self.image = load_image(image, -1)

    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[2] + self.rect[0] and (
                self.rect[1] <= pos[1] <= self.rect[3] + self.rect[1]):
            return True
        return False

    def run(self, obj, tick, reverse=False, ma=False):
        if obj.new_coords[1] - self.new_coords[1] == 0:
            b = 0
            a = self.velocity * tick if self.new_coords[0] < obj.new_coords[0] else -self.velocity * tick
        elif -1 <= self.new_coords[0] - obj.new_coords[0] <= 1:
            b = self.velocity * tick if self.new_coords[1] < obj.new_coords[1] else -self.velocity * tick
            a = 0
        else:
            b = ((self.velocity * tick)**2 / (
                    1 + ((obj.new_coords[0] - self.new_coords[0]) / (obj.new_coords[1] - self.new_coords[1])) ** 2))**0.5
            if obj.new_coords[1] < self.new_coords[1]:
                b = -b
            a = b * (obj.new_coords[0] - self.new_coords[0]) / (obj.new_coords[1] - self.new_coords[1])
        if reverse:
            b, a = -b, -a
        if ma:
            a /= self.mass
            b /= self.mass

        self.new_coords = min(max(0, self.new_coords[0] + a), sizeX - self.rect[2]), min(
            max(self.new_coords[1] + b, 0), sizeY - self.rect[3])



    def update(self, *args):
        self.rect[:2] = self.new_coords





class King(Figure):
    def __init__(self, group, pos):
        super().__init__(group, pos, kingImage, 200, 20)

    def get_name(self):
        return 'King'


    def ask_setting(self):
        if len(self.attack) < 3:
            return 'Определите порядок аттаки'
        if self.radius == -1:
            return 'Выберите диапазон, начиная с которого король будет отступать'
        return 'ОК'

    def set_aims(self, aim):
        if (aim.get_name() == 'Aristocrat' or aim.get_name() == 'King') and aim not in self.attack:
            self.attack.append(aim)
            if len(self.attack) == 3:
                return len(self.attack), True
            return len(self.attack), False
        return False, False

    def move(self, tick):
        need_run = {}
        for i in self.opposition:
            if i.get_name() == 'Soldier' and (
                    i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2 <= self.radius ** 2:
                need_run[(i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2] = i
        if bool(need_run):
            self.run(need_run[min(need_run)], tick, reverse=True)
        else:
            while bool(self.attack) and self.attack[0] not in self.opposition:
                del self.attack[0]
            if bool(self.attack):
                self.run(self.attack[0], tick)



class Aristocrat(Figure):
    def __init__(self, group, pos):
        super().__init__(group, pos, aristocratImage, 100, 5)
        self.resultant = (self.rect[0], self.rect[1])



    def ask_setting(self):
        if len(self.attack) < 6:
            return 'Определите порядок аттаки'
        if self.radius == -1:
            return 'Выберите диапазон, начиная с которого аристократ будет отступать'
        return 'ОК'

    def get_name(self):
        return 'Aristocrat'

    def set_aims(self, aim):
        if (aim.get_name() == 'Soldier' or aim.get_name() == 'Aristocrat') and aim not in self.attack:
            self.attack.append(aim)
            if len(self.attack) == 6:
                return len(self.attack), True
            return len(self.attack), False
        return False, False

    def move(self, tick):
        need_run = {}
        for i in self.opposition:
            if i.get_name() == 'King' and (
                    i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2 <= self.radius ** 2:
                need_run[(i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2] = i
        if bool(need_run):
            self.run(need_run[min(need_run)], tick, reverse=True)
        else:
            while bool(self.attack) and self.attack[0] not in self.opposition:
                del self.attack[0]
            if bool(self.attack):
                self.run(self.attack[0], tick)



class Soldier(Figure):
    def __init__(self, group, pos):
        super().__init__(group, pos, soldierImage, 50, 2)

    def get_name(self):
        return 'Soldier'

    def ask_setting(self):
        if len(self.attack) < 5:
            return 'Определите порядок аттаки'
        if self.radius == -1:
            return 'Выберите диапазон, начиная с которого простолюдин будет отступать'
        return 'ОК'

    def set_aims(self, aim):
        if (aim.get_name() == 'Soldier' or aim.get_name() == 'King') and aim not in self.attack:
            self.attack.append(aim)
            if len(self.attack) == 5:
                return len(self.attack), True
            return len(self.attack), False
        return False, False


    def move(self, tick):
        need_run = {}
        for i in self.opposition:
            if i.get_name() == 'Aristocrat' and (
                    i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2 <= self.radius ** 2:
                need_run[(i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2] = i
        if bool(need_run):
            self.run(need_run[min(need_run)], tick, reverse=True)
        else:
            while bool(self.attack) and self.attack[0] not in self.opposition:
                del self.attack[0]
            if bool(self.attack):
                self.run(self.attack[0], tick)


class Diapason(pygame.sprite.Sprite):
    def __init__(self, group, pos, image, radius):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect[:2] = pos
        self.radius = radius
        # self.velocity = 10

    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[2] + self.rect[0] and (
                self.rect[1] <= pos[1] <= self.rect[3] + self.rect[1]):
            return True
        return False


pygame.init()
sizeX, sizeY = 800, 600
screen = pygame.display.set_mode((sizeX, sizeY))
player = pygame.sprite.Group()
evil = pygame.sprite.Group()
kingImage, soldierImage = load_image('king.png', -1), load_image('soldier.png', -1)
aristocratImage = load_image('aristocrat.png', -1)
king = King(player, (700, 300))
aristocrat1 = Aristocrat(player, (600, 200))
''''''
aristocrat2 = Aristocrat(player, (600, 400))
soldier1 = Soldier(player, (500, 100))
soldier2 = Soldier(player, (500, 225))
soldier3 = Soldier(player, (500, 350))
soldier4 = Soldier(player, (500, 475))
''''''

King(evil, (100, 300)).set_image('kinge.png')
Aristocrat(evil, (200, 200)).set_image('aristocrate.png')
Aristocrat(evil, (200, 400)).set_image('aristocrate.png')
Soldier(evil, (300, 100)).set_image('soldiere.png')
Soldier(evil, (300, 225)).set_image('soldiere.png')
Soldier(evil, (300, 350)).set_image('soldiere.png')
Soldier(evil, (300, 475)).set_image('soldiere.png')


screen2 = pygame.Surface(aristocrat1.image.get_size())
running = True
need_setting = [king, aristocrat1, aristocrat2, soldier1, soldier2, soldier3, soldier4]
# need_setting = [king, aristocrat1]
diapason = pygame.sprite.Group()
Diapason(diapason, (25, 10), load_image('40.png'), 40)
Diapason(diapason, (175, 10), load_image('80.png'), 80)
Diapason(diapason, (325, 10), load_image('120.png'), 120)
Diapason(diapason, (475, 10), load_image('160.png'), 160)
Diapason(diapason, (625, 10), load_image('200.png'), 200)
should_write = []
moving = False
ok, full, choose_diapason = False, False, False
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not moving and event.type == pygame.MOUSEBUTTONDOWN:
            if choose_diapason:
                for i in diapason:
                    if i.get_click(event.pos):
                        need_setting[0].radius = i.radius
                        del need_setting[0]
                        if len(need_setting) == 0:
                            moving = True
                            clock = pygame.time.Clock()
                            for i in evil:
                                if i.get_name() == 'King':
                                    # i.attack = [aristocrat1, king]
                                    i.attack = random.shuffle([aristocrat1, aristocrat2, king])
                                    # random.shuffle(i.attack)
                                if i.get_name() == 'Aristocrat':
                                    i.attack = random.shuffle(
                                        [aristocrat1, aristocrat2, soldier1, soldier2, soldier3, soldier3])
                                    # i.attack = [aristocrat1]
                                    '''i.attack = random.shuffle(
                                        [aristocrat1])'''
                                if i.get_name() == 'Soldier':
                                    i.attack = random.shuffle(
                                        [king, soldier1, soldier2, soldier3, soldier3])
                                    # i.attack = [king]
                                # i.radius = random.choice([40, 80, 120, 160, 200])
                                i.radius = random.choice([40, 80, 120, 160, 200])
                        # print(choose_diapason, need_setting)
                        should_write = []
                        choose_diapason = False
            elif bool(need_setting):
                for i in evil:
                    if i.get_click(event.pos):
                        ok, full = need_setting[0].set_aims(i)
                        # print(ok, full)
                        if full:
                            choose_diapason = True
                            '''del need_setting[0]
                            should_write = []'''
                        if ok:
                            should_write.append([i.rect[:2],  str(ok)])

    if len(need_setting) > 0:
        write((100, 550), need_setting[0].ask_setting())
        screen2.fill((0, 255, 0))
        screen.blit(screen2, (need_setting[0].rect[:2]))
    if moving:
        tick = clock.tick() / 1000
        for i in player:
            # print(i.get_name(), len(i.attack))
            i.move(tick)
        for i in evil:
            i.move(tick)
        player.update()
        evil.update()
        for i in player:
            player.remove(i)
            for j in pygame.sprite.spritecollide(i, player, False):
                i.run(j, 0.5, reverse=True, ma=True)
            player.add(i)
        player.update()
        for i in evil:
            # print(i.attack)
            evil.remove(i)
            if pygame.sprite.spritecollideany(i, evil):
                # print(i)
                for j in pygame.sprite.spritecollide(i, evil, False):
                    i.run(j, 0.5, reverse=True, ma=True)
            evil.add(i)
        evil.update()
        for i in player:
            if pygame.sprite.spritecollideany(i, evil):
                for j in pygame.sprite.spritecollide(i, evil, False):
                    if j in i.attack:
                        if j.get_name() == i.get_name():
                            delet = random.choice([i, j])
                            if delet == i:
                                player.remove(i)
                            else:
                                evil.remove(j)
                        else:
                            evil.remove(j)
                    else:
                        player.remove(i)

    player.draw(screen)
    evil.draw(screen)
    for i in should_write:
        write(i[0], i[1])
    if choose_diapason:
        diapason.draw(screen)
    pygame.display.flip()
