import pygame, os, random, ctypes, sys
os.environ['SDL_VIDEO_CENTERED'] = '1'


def write(position, text, size=20):
    # Функция отвечает за вывод текстовой информации на экран
    font = pygame.font.SysFont('Times New Roman', size)
    text = font.render(str(text), 1, (255, 255, 255))
    screen.blit(text, position)


def load_image(name, colorkey=None, local_path=''):
    # Функция отвечает за загрузку изображений
    fullname = os.path.join('data', local_path, name)
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
    # Общий класс для всех фигур
    def __init__(self, group, pos, image, velocity, mass, player, evil):
        super().__init__(group)
        self.indexAttack = 0
        self.mass = mass
        self.velocity = velocity
        self.opposition = player if group is evil else evil
        self.image = image
        self.rect = self.image.get_rect()
        self.startPos = pos
        self.rect[:2] = pos
        self.new_coords = list(pos)
        self.attack = []
        self.radius = -1

    def restart(self, opposite):
        # Функция перезагруски. Вызывается при завершении одного раунда, возвращает фигуру на исходную позицию
        self.rect[:2] = self.startPos
        self.new_coords = list(self.startPos)
        self.indexAttack = 0
        self.opposition = opposite

    def set_image(self, image, localpath):
        # Изменение изображения фигуры. Применяется для фигур противника
        self.image = load_image(image, -1, localpath)

    def get_click(self, pos):
        # Проверка того, что на фигуру нажали
        if self.rect[0] - 10 <= pos[0] <= self.rect[2] + self.rect[0] + 10 and (
                self.rect[1] - 10 <= pos[1] <= self.rect[3] + self.rect[1] + 10):
            return True
        return False

    def run(self, obj, tick, reverse=False, ma=False):
        # Функция автоматического движения фигуры
        # Фигура движется в направлении 
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

        self.new_coords = [min(max(0, self.new_coords[0] + a), sizeX - self.rect[2]), min(
            max(self.new_coords[1] + b, 0), sizeY - self.rect[3])]

    def update(self, *args):
        self.rect[:2] = self.new_coords


class King(Figure):
    def __init__(self, group, pos, player, evil):
        super().__init__(group, pos, load_image('king.png', -1, localpath), 400, 20, player, evil)

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
        try:
            need_run = {}
            for i in self.opposition:
                if i.get_name() == 'Soldier' and (
                        i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2 <= self.radius ** 2:
                    need_run[(i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2] = i
            if bool(need_run):
                self.run(need_run[min(need_run)], tick, reverse=True)
            else:
                while len(self.attack) > self.indexAttack and self.attack[self.indexAttack] not in self.opposition:
                    self.indexAttack += 1
                if len(self.attack) > self.indexAttack:
                    self.run(self.attack[self.indexAttack], tick)
        except Exception as e:
            print(e)


class Aristocrat(Figure):
    def __init__(self, group, pos, player, evil):
        super().__init__(group, pos, load_image('aristocrat.png', -1, localpath), 200, 5, player, evil)
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
        try:
            need_run = {}
            for i in self.opposition:
                if i.get_name() == 'King' and (
                        i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2 <= self.radius ** 2:
                    need_run[(i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2] = i
            if bool(need_run):
                self.run(need_run[min(need_run)], tick, reverse=True)
            else:
                while len(self.attack) > self.indexAttack and self.attack[self.indexAttack] not in self.opposition:
                    self. indexAttack += 1
                if len(self.attack) > self.indexAttack:
                    self.run(self.attack[self.indexAttack], tick)
        except Exception as e :
            print(e)


class Soldier(Figure):
    def __init__(self, group, pos, player, evil):
        super().__init__(group, pos, load_image('soldier.png', -1, localpath), 100, 2, player, evil)

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
        try:
            need_run = {}
            for i in self.opposition:
                if i.get_name() == 'Aristocrat' and (
                        i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2 <= self.radius ** 2:
                    need_run[(i.rect[0] - self.rect[0]) ** 2 + (i.rect[1] - self.rect[1]) ** 2] = i
            if bool(need_run):
                self.run(need_run[min(need_run)], tick, reverse=True)
            else:
                while len(self.attack) > self.indexAttack and self.attack[self.indexAttack] not in self.opposition:
                    self.indexAttack += 1
                if len(self.attack) > self.indexAttack:
                    self.run(self.attack[self.indexAttack], tick)
        except Exception as e:
            print(e)

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


class SkinMenu(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('skinMenu.png')
        self.rect = self.image.get_rect()
        self.rect[0] = sizeX - self.rect[2]
        self.rect[1] = sizeY - self.rect[3]
        self.level = 0

    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] \
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]:
            return True

    def get_name(self):
        return 'SkinMenu'


class ButtonStart(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('buttonStart.png', -1)
        self.rect = self.image.get_rect()
        self.rect[0] = (sizeX - self.rect[2]) // 2
        self.rect[1] = (sizeY - self.rect[3]) // 2
    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] \
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]:
            return True

    def get_name(self):
        return 'ButtonStart'


class Sound(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.sounds = [load_image('sound100.png', -1), load_image('sound75.png', -1),
                       load_image('sound50.png', -1), load_image('sound25.png', -1),
                       load_image('sound0.png', -1)]
        self.index = 0
        self.image = self.sounds[self.index]
        self.rect = self.image.get_rect()
        self.rect[1] = sizeY - self.rect[3]

    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] \
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]:
            self.index = (self.index + 1) % 5
            self.image = self.sounds[self.index]
            return 1 - self.index * 0.25
        return sound_volume

    def get_name(self):
        return 'Sound'


class Skin(pygame.sprite.Sprite):
    def __init__(self, group, pos, localpath, points):
        super().__init__(group)
        self.localpath = localpath
        self.points = points
        self.image = load_image('king.png', -1, localpath)
        self.rect = self.image.get_rect()
        self.rect[:2] = pos
        font = pygame.font.SysFont('Times New Roman', 20)
        self.text = font.render(str(points), 1, (255, 255, 255), (15, 155, 200))
        self.w = max(self.rect[2], self.text.get_size()[0])
        self.h = self.rect[3] + self.text.get_size()[1]
        self.bought = False

    def get_click(self, pos, points, answer, localpath):
        if self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] \
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]:
            if self.bought:
                return self.localpath, 'OK', points
            if points >= self.points:
                self.bought = True
                return self.localpath, 'OK', points - self.points
            return localpath, 'НЕ ХВАТАЕТ ОЧКОВ', points
        return localpath, answer, points

    def get_name(self):
        return 'Skin'


class Exit(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('exit.png', None)
        self.rect = self.image.get_rect()
    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] \
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]:
            return True

    def get_name(self):
        return 'Exit'

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Rules(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image('rules.png', -1)
        self.rect = self.image.get_rect()
        self.rect[0] = sizeX - self.rect[2]

    def get_click(self, pos):
        if self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] \
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]:
            return True

    def get_name(self):
        return 'Rules'


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, name):
        super().__init__(particles_sprites)
        self.image = load_image(name, -1)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.startX, self.startY = pos

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        # print(self.velocity)
        if (self.startX - self.rect.x) ** 2 + (self.startY - self.rect.y) ** 2 > 900:
            self.kill()


def setting(player, evil):
    w, h = load_image('king.png', -1, localpath).get_size()
    King(evil, (w, int(sizeY / 2 - h / 2)), player, evil).set_image('kinge.png', localpath)
    Aristocrat(evil, (3 * w, int(sizeY / 3 - h / 2)), player, evil).set_image('aristocrate.png', localpath)
    Aristocrat(evil, (3 * w, int(2 * sizeY / 3 - h / 2)), player, evil).set_image('aristocrate.png', localpath)
    Soldier(evil, (5 * w, int(sizeY / 5 - h / 2)), player, evil).set_image('soldiere.png', localpath)
    Soldier(evil, (5 * w, int(2 * sizeY / 5 - h / 2)), player, evil).set_image('soldiere.png', localpath)
    Soldier(evil, (5 * w, int(3 * sizeY / 5 - h / 2)), player, evil).set_image('soldiere.png', localpath)
    Soldier(evil, (5 * w, int(4 * sizeY / 5 - h / 2)), player, evil).set_image('soldiere.png', localpath)
    king, aristocrat1, aristocrat2, soldier1, soldier2, soldier3, soldier4 = \
        King(player, (sizeX - 2 * w, int(sizeY / 2 - h / 2)), player, evil), \
        Aristocrat(player, (sizeX - 4 * w, int(sizeY / 3 - h / 2)), player, evil), \
        Aristocrat(player, (sizeX - 4 * w, int(2 * sizeY / 3 - h / 2)), player, evil),\
        Soldier(player, (sizeX - 6 * w, int(sizeY / 5 - h / 2)), player, evil), \
        Soldier(player, (sizeX - 6 * w, int(2 * sizeY / 5 - h / 2)), player, evil),\
        Soldier(player, (sizeX - 6 * w, int(3 * sizeY / 5 - h / 2)), player, evil), \
        Soldier(player, (sizeX - 6 * w, int(4 * sizeY / 5 - h / 2)), player, evil)
    for i in evil:
        if i.get_name() == 'King':
            i.attack = [aristocrat1, aristocrat2, king]
        if i.get_name() == 'Aristocrat':
            i.attack = [aristocrat1, aristocrat2, soldier1, soldier2, soldier3, soldier4]
        if i.get_name() == 'Soldier':
            i.attack = [king, soldier1, soldier2, soldier3, soldier4]
    return [king, aristocrat1, aristocrat2, soldier1, soldier2, soldier3, soldier4]


def evilShuffle(evil):
    for i in evil:
        random.shuffle(i.attack)
        i.radius = random.choice([40, 80, 120, 160, 200])


def showResult():
    if should_write[0][1] < 0:
        loseSound.play()
        pygame.draw.rect(screen, (255, 0, 0), (3 * sizeX // 8, 3 * sizeY // 8, sizeX // 4, sizeY // 4))
    elif should_write[0][1] == 0:
        loseSound.play()
        pygame.draw.rect(screen, (0, 0, 255), (3 * sizeX // 8, 3 * sizeY // 8, sizeX // 4, sizeY // 4))
    else:
        winSound.play()
        pygame.draw.rect(screen, (0, 255, 0), (3 * sizeX // 8, 3 * sizeY // 8, sizeX // 4, sizeY // 4))
    font = pygame.font.SysFont('Times New Roman', 30)
    text = font.render('points: ' + str(should_write[0][1]), 1, (255, 255, 255))
    screen.blit(text, (3 * sizeX // 8 + (sizeX // 4 - text.get_rect()[2]) // 2,
                       3 * sizeY // 8 + (sizeY // 8 - text.get_rect()[3]) // 2))
    text = font.render('level: ' + str(level), 1, (255, 255, 255))
    screen.blit(text, (3 * sizeX // 8 + (sizeX // 4 - text.get_rect()[2]) // 2,
                       4 * sizeY // 8 + (sizeY // 8 - text.get_rect()[3]) // 2))


def set_skins(number):
    startX, startY = 100, 100
    for i in range(number):
        skin = Skin(skins, (startX, startY), str(i), i * 5000)
        if startX + 100 + 2 * skin.w > sizeX:
            startX = 100
            startY += 100 + skin.h
        else:
            startX += skin.w + 100
        if bought.get(str(i), 'False') == 'True':
            skin.bought = True


def create_particles(position, name):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        i, j = random.choice(numbers), random.choice(numbers)
        while i == j == 0:
            i, j = random.choice(numbers), random.choice(numbers)
        Particle(position, i, j, name)


def terminate():
    file = open('data/result.txt', mode='w')
    file.write(str(points) + ' ' + str(level))
    file.close()
    file = open('data/bought.txt', mode='w')
    for i in skins:
        if i.get_name() != 'Exit':
            file.writelines(i.localpath + ' ' + str(i.bought) + '\n')
    file.close()
    pygame.quit()
    sys.exit()


def skin_screen(points, localpath):
    answer = ''
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_particles(event.pos, 'star.png')
                for i in skins:
                    if i.get_name() == 'Exit':
                        if i.get_click(event.pos):
                            return points, localpath
                    else:
                        localpath, answer, points = i.get_click(event.pos, points, answer, localpath)
        particles_sprites.update()
        particles_sprites.draw(screen)
        skins.draw(screen)
        for i in skins:
            if i.get_name() != 'Exit':
                screen.blit(i.text, (i.rect[0], i.rect[1] + i.rect[3]))
        write((10, sizeY - 100), answer, 50)
        write((sizeX // 2, 0), str(points), size=50)
        pygame.display.flip()


def rules_screen():
    rules = ['Игра "Семь"',
             'В данной игре в вашем распоряжении 7 фигур: 1 король, 2 аристократа, 4 простолюдина',
             'Цель игры - уничтожить все фигуры противника с минимальными потерями',
             'При начале игры нужно указать порядок аттаки и диапазон отступления для каждой фигуры',
             'Король нападает на вражеских короля и аристократов',
             'Аристократ - на вражеских аристократов и простолюдинов',
             'Простолюдин - на вражеских простолюдинов и короля',
             'Игрок управляет одной из 7 фигур, остальные фигуры движутся согласно указанному порядку аттаки',
             'Между фигурами можно переключаться при помощи клавиши пробела',
             'В каждом раунде по 12 игр в которых выбранный порядок аттаки остается неизменным',
             'По истечении 12 игр, подводится итог в баллах',
             'За уничтожение вражеского короля прибавляется 800 баллов, за потерю своего - вычитается',
             'За уничтожение вражеского аристократа прибавляется 400 баллов, за потерю своего - вычитается',
             'За уничтожение вражеского солдата прибавляется 200 баллов, за потерю своего - вычитается',
             'Если за раунд игрок ушел в плюс, то он переходит на следующий уровень,',
             'баллы прибавляются к общему счету',
             'Король движется в 2 раза быстрее аристократа и в 4 раза быстрее простолюдина',
             'Если фигурой управляет игрок, то ее скорость увеличивается']
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_particles(event.pos, 'star.png')
                return
        for i in range(len(rules)):
            write((20, i * 40), rules[i], size=25)
        particles_sprites.update()
        particles_sprites.draw(screen)
        pygame.display.flip()


def setting_screen(player, evil, playerList, screen2, should_write):
    need_setting = playerList.copy()
    clock.tick()
    ok, full, choose_diapason = False, False, False
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_particles(event.pos, 'star.png')
                if choose_diapason:
                    for i in diapason:
                        if i.get_click(event.pos):
                            need_setting[0].radius = i.radius
                            del need_setting[0]
                            del should_write[1:]
                            choose_diapason = False
                            if len(need_setting) == 0:
                                clock.tick()
                                return False
                elif bool(need_setting):
                    for i in evil:
                        if i.get_click(event.pos):
                            ok, full = need_setting[0].set_aims(i)
                            if full:
                                choose_diapason = True
                            if ok:
                                should_write.append([(i.rect[0] - 10, i.rect[1]), str(ok)])
                if exit.get_click(event.pos):
                    del should_write[1:]
                    return True

        particles_sprites.update()
        particles_sprites.draw(screen)
        write((50, int(4 * sizeY / 5 + playerList[0].image.get_size()[1])), need_setting[0].ask_setting())
        screen2.fill((0, 255, 0))
        screen.blit(screen2, (need_setting[0].rect[:2]))
        exit.draw(screen)
        player.draw(screen)
        evil.draw(screen)
        for i in range(len(should_write)):
            write(should_write[i][0], should_write[i][1], size=50) if i == 0 else write(
                should_write[i][0], should_write[i][1])
        if choose_diapason:
            diapason.draw(screen)
        pygame.display.flip()


def game_screen(points, level):
    player = pygame.sprite.Group()
    evil = pygame.sprite.Group()
    playerList = setting(player, evil)
    evilList = [i for i in evil]
    evilShuffle(evil)
    index = 0
    screen2 = pygame.Surface(playerList[0].image.get_size())
    if setting_screen(player, evil, playerList, screen2, should_write):
        return points, level
    was = 0
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                index = (index + 1) % len(playerList)
                while playerList[index] not in player:
                    index = (index + 1) % len(playerList)
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_particles(event.pos, 'star.png')
                if exit.get_click(event.pos):
                    return points, level
        particles_sprites.update()
        particles_sprites.draw(screen)
        tick = clock.tick() / 1000
        keys = pygame.key.get_pressed()
        while playerList[index] not in player:
            index = (index + 1) % len(playerList)
        if keys[pygame.K_DOWN]:
            playerList[index].new_coords[1] += tick * playerList[index].velocity
        if keys[pygame.K_UP]:
            playerList[index].new_coords[1] -= tick * playerList[index].velocity * 2
        if keys[pygame.K_RIGHT]:
            playerList[index].new_coords[0] += tick * playerList[index].velocity * 2
        if keys[pygame.K_LEFT]:
            playerList[index].new_coords[0] -= tick * playerList[index].velocity * 2
        if playerList[index].new_coords[0] > sizeX - playerList[index].rect[2]:
            playerList[index].new_coords[0] = sizeX - playerList[index].rect[2]
        elif playerList[index].new_coords[0] < 0:
            playerList[index].new_coords[0] = 0
        if playerList[index].new_coords[1] > sizeY - playerList[index].rect[3]:
            playerList[index].new_coords[1] = sizeY - playerList[index].rect[3]
        elif playerList[index].new_coords[1] < 0:
            playerList[index].new_coords[1] = 0
        for i in player:
            if i != playerList[index]:
                i.move(tick)
        for i in evil:
            i.move(tick)
        player.update()
        evil.update()
        for i in player:
            if i != playerList[index]:
                player.remove(i)
                for j in pygame.sprite.spritecollide(i, player, False):
                    collisionSound.play()
                    i.run(j, 0.5, reverse=True, ma=True)
                player.add(i)
        player.update()
        for i in evil:
            evil.remove(i)
            if pygame.sprite.spritecollideany(i, evil):
                for j in pygame.sprite.spritecollide(i, evil, False):
                    collisionSound.play()
                    i.run(j, 0.5, reverse=True, ma=True)
            evil.add(i)
        evil.update()
        for i in player:
            if pygame.sprite.spritecollideany(i, evil):
                for j in pygame.sprite.spritecollide(i, evil, False):
                    collisionSound.play()
                    if j in i.attack:
                        if j.get_name() == i.get_name():
                            delet = random.choice([i, j])
                            if delet == i:
                                player.remove(i)
                                create_particles(i.rect[:2], 'killStar.png')
                                should_write[0][1] -= i.velocity * 2
                            else:
                                should_write[0][1] += j.velocity * 2
                                create_particles(j.rect[:2], 'killStar.png')
                                evil.remove(j)
                        else:
                            should_write[0][1] += j.velocity * 2
                            create_particles(j.rect[:2], 'killStar.png')
                            evil.remove(j)
                    else:
                        create_particles(i.rect[:2], 'killStar.png')
                        should_write[0][1] -= i.velocity * 2
                        player.remove(i)
        screen2.fill((100, 100, 100))
        screen.blit(screen2, playerList[index].rect[:2])
        if len(player) == 0 or len(evil) == 0:
            index = 0
            was += 1
            player, evil = pygame.sprite.Group(), pygame.sprite.Group()
            if was == 12:
                points = max(points + should_write[0][1], 0)
                if should_write[0][1] > 0:
                    level += 1
                if finish_screen():
                    return points, level
                clock.tick()
                pygame.mixer.music.play(-1)
                player = pygame.sprite.Group()
                evil = pygame.sprite.Group()
                playerList = setting(player, evil)
                evilList = [i for i in evil]
                evilShuffle(evil)
                was = 0
                should_write[0][1] = 0
                if setting_screen(player, evil, playerList, screen2, should_write):
                    return points, level
            else:
                for i in playerList:
                    i.restart(evil)
                    player.add(i)
                for i in evilList:
                    i.restart(player)
                    evil.add(i)
                evilShuffle(evil)
        exit.draw(screen)
        player.draw(screen)
        evil.draw(screen)
        for i in range(len(should_write)):
            write(should_write[i][0], should_write[i][1], size=50) if i == 0 else write(
                should_write[i][0], should_write[i][1])
        exit.draw(screen)
        pygame.display.flip()


def finish_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_particles(event.pos, 'star.png')
                return exit.get_click(event.pos)
        pygame.mixer.music.fadeout(2000)
        showResult()
        exit.draw(screen)
        pygame.display.flip()


pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('data/backgroundMusic.mp3')
pygame.mixer.music.play(-1)
collisionSound = pygame.mixer.Sound('data/collision.wav')
winSound = pygame.mixer.Sound('data/win2.wav')
loseSound = pygame.mixer.Sound('data/lose.wav')
winSound.set_volume(0.5)
sound_volume = 1
localpath = '0'
sizeX, sizeY = ctypes.windll.user32.GetSystemMetrics(0) - 100, ctypes.windll.user32.GetSystemMetrics(1) - 100
screen = pygame.display.set_mode((sizeX, sizeY))
menu = pygame.sprite.Group()
skins = pygame.sprite.Group()
particles_sprites = pygame.sprite.Group()
SkinMenu(menu)
ButtonStart(menu)
Sound(menu)
Rules(menu)
file = open('data/result.txt', mode='r')
points, level = map(int, file.read().split())
file.close()
file = open('data/bought.txt', mode='r')
readFile = file.read().split('\n')
file.close()
bought = {}
for i in readFile:
    if len(i) != 0:
        bought[i.split()[0]] = i.split()[1]
running = True
diapason = pygame.sprite.Group()
Diapason(diapason, (125, 0), load_image('40.png'), 40)
Diapason(diapason, (275, 0), load_image('80.png'), 80)
Diapason(diapason, (425, 0), load_image('120.png'), 120)
Diapason(diapason, (575, 0), load_image('160.png'), 160)
Diapason(diapason, (725, 0), load_image('200.png'), 200)
should_write = [[(sizeX // 2, 0), 0]]
index = 0
was = 0
state = 3
ok, full, choose_diapason = False, False, False
clock = pygame.time.Clock()
set_skins(17)
exit = Exit(skins)
background = pygame.transform.scale(load_image('newbackground.jpg'), (sizeX, sizeY))
while running:
    screen.fill((100, 100, 100))
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            create_particles(event.pos, 'star.png')
            should_write = [should_write[0]]
            should_write[0][1] = 0
            answer = ''
            for i in menu:
                if i.get_name() == 'Sound':
                    sound_volume = i.get_click(event.pos)
                    pygame.mixer.music.set_volume(sound_volume)
                    winSound.set_volume(0.5 * sound_volume)
                    collisionSound.set_volume(sound_volume)
                    loseSound.set_volume(sound_volume)
                elif i.get_click(event.pos):
                    if i.get_name() == 'SkinMenu':
                        points, localpath = skin_screen(points, localpath)
                    elif i.get_name() == 'Rules':
                        rules_screen()
                    elif i.get_name() == 'ButtonStart':
                        points, level = game_screen(points, level)
    particles_sprites.update()
    particles_sprites.draw(screen)
    menu.draw(screen)
    write((0, 0), 'points: ' + str(points), size=50)
    write((0, 100), 'level: ' + str(level), size=50)
    pygame.display.flip()
