import math
import random
import sys
import pygame
from pygame import mixer
import copy

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
background = pygame.image.load('background.png')
boom = pygame.image.load('boom.png')
pygame.mixer.music.load("Putty_Water.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)
paused = False
over_game = False
score_value = 0
font = pygame.font.Font(pygame.font.get_default_font(), 32)
over_font = pygame.font.Font(pygame.font.get_default_font(), 64)
star_cantbe = False
power_up = 0
time_elapsed_since_last_action = 0
boss_laser_sound = 0
time_elapsed_since_last_action2 = 0
time_elapsed_since_last_action3 = 0
current_state = 0
begone = False
was_boss = False
from_pause = False
pause_laser = 0
pause_laser_end = 0
dt = clock.tick()
xyz = 0
boss_phase = 0
destroyed = 0

class Player:
    def __init__(self):
        self.playerImg = pygame.image.load('player.png')
        self.playerX = 370
        self.playerY = 480
        self.playerX_change = 0

class Enemy:
    def __init__(self, paused):
        self.enemyImg = []
        self.enemyY_change = []
        self.num_of_enemies = 6
        for i in range(self.num_of_enemies):
            self.enemyImg.append(pygame.image.load('enemy.png'))
            self.enemyY_change.append(40)
        if paused == False:
            self.enemyX = []
            self.enemyY = []
            self.enemyX_change = []
            for i in range(self.num_of_enemies):
                self.enemyX.append(random.randint(0, 736))
                self.enemyY.append(random.randint(50, 150))
                self.enemyX_change.append(6)

class Bullet:
    def __init__(self):
        self.bulletImg = pygame.image.load('bullet.png')
        self.bulletX = 0
        self.bulletY = 480
        self.bulletX_change = 0
        self.bulletY_change = 10
        self.bullet_state = "ready"

class Star:
    def __init__(self):
        self.starImg = pygame.image.load('star.png')
        self.starX = 2000
        self.starY = 2000
        self.starX_change = 0
        self.starY_change = 0.3

class Boss:
    def __init__(self):
        self.bossImg = pygame.image.load('alien.png')
        self.boss_laserImg = pygame.image.load('laserphotoAid-removed-background (1).png')
        self.bossX = 800
        self.bossY = 40
        self.bossX_change = 0
        self.bossY_change = 0
        self.current_hp = 200
        self.max_hp = 200
        self.target_hp = 200
        self.hp_length = 200
        self.hp_height = 20
        self.hp_width = 200
        self.hp_change = 1

    def update(self):
        # self.basic_health()
        self.advanced_health()

    def get_damage(self, amount):
        if self.target_hp > 0:
            self.target_hp -= amount
        if self.target_hp <= 0:
            self.target_hp = 0

    # def basic_health(self):
    #     pygame.draw.rect(screen, (255, 0, 0), (590, 10, self.target_hp, self.hp_height))
    #     pygame.draw.rect(screen, (255, 255, 255), (590, 10, self.target_hp, self.hp_height), 4)

    def advanced_health(self):
        transition_width = 0
        transition_color = (255, 0, 0)
        if self.current_hp > self.target_hp:
            self.current_hp -= self.hp_change
            transition_width = self.target_hp - self.current_hp
            transition_color = (255, 255, 0)
        hp_adv_bar = pygame.Rect(590, 10, self.current_hp, self.hp_height)
        transition_bar = pygame.Rect(hp_adv_bar.right, 10, transition_width, self.hp_height)
        pygame.draw.rect(screen, (255, 0, 0), hp_adv_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255, 255, 255), (590, 10, self.hp_width, self.hp_height), 4)

def show_score(x, y):
    global score_value
    score = font.render("Press Esc to pause, SCORE : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    global high_score, over_game, power_up
    power_up = 0
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 100))
    score_after = font.render("YOUR SCORE: " + str(high_score), True, (255, 255, 255))
    screen.blit(score_after, (265, 188))

def player(x, y, player1):
    screen.blit(player1.playerImg, (x, y))

def enemy(x, y, i, enemy1):
    screen.blit(enemy1.enemyImg[i], (x, y))

def boss(x, y, boss1):
    screen.blit(boss1.bossImg, (x, y))

def boss_colision(boss1, player1):
    global boss_laser_var, boom, time_elapsed_since_last_action2, dt, high_score,\
        was_boss, score_value, over_game, star_cantbe, paused, begone, current_state
    distance_from_laser = math.sqrt(math.pow((boss1.bossX + 100) - player1.playerX, 2) + (
        math.pow(player1.playerY - player1.playerY, 2)))
    if distance_from_laser <= 84:
        current_state = 1
        begone = True
    if begone == True:
        screen.blit(boom, (player1.playerX, player1.playerY))
        player1.playerY = 2000
        boss_laser_var.set_volume(0)
        high_score = copy.deepcopy(score_value)
        score_value = 0
        begone = False
        over_game = True
        star_cantbe = True
        paused = False
        was_boss = True
        game_over()

def boss_laser(x, y, boss1):
    global time_elapsed_since_last_action, dt, clock, boss_laser_sound, boss_laser_var,\
        time_elapsed_since_last_action2, from_pause, pause_laser_end, time_elapsed_since_last_action3, xyz, boss_phase
    dns = clock.tick()
    boss_angry = mixer.Sound('angryshorter.wav')
    boss_angry.set_volume(0.8)
    if pause_laser_end == 0:
        time_elapsed_since_last_action = copy.deepcopy(xyz)
        pause_laser_end += 1
        xyz = 0
    time_elapsed_since_last_action += dt
    if boss1.current_hp >= (boss1.max_hp * 0.66):
        if time_elapsed_since_last_action > 1000:
            screen.blit(boss1.boss_laserImg, (x + 42, y + 256))
            boss_laser_var = mixer.Sound('laser-5.wav')
            boss_laser_var.set_volume(0.1)
            if boss_laser_sound == 0:
                boss_laser_var.play(1)
            boss_laser_sound += 1
            boss_colision(boss1, player1)
            if time_elapsed_since_last_action > 3000:
                boss_laser_sound = 0
                time_elapsed_since_last_action = 0
    elif boss1.current_hp > (boss1.max_hp * 0.33) and boss1.current_hp < (boss1.max_hp * 0.66):
        if boss_phase == 0:
            boss_angry.play(0)
            boss_phase += 1
        boss1.bossX_change *= 2
        if time_elapsed_since_last_action > 1000:
            boss1.bossX_change /= 2
            screen.blit(boss1.boss_laserImg, (x + 42, y + 256))
            boss_laser_var = mixer.Sound('laser-5.wav')
            boss_laser_var.set_volume(0.1)
            if boss_laser_sound == 0:
                boss_laser_var.play(1)
            boss_laser_sound += 1
            boss_colision(boss1, player1)
            if time_elapsed_since_last_action > 3000:
                boss_laser_sound = 0
                time_elapsed_since_last_action = 0
    elif boss1.current_hp <= (boss1.max_hp * 0.33):
        if boss_phase == 1:
            boss_angry.play(0)
            boss_phase += 1
            time_elapsed_since_last_action = -200
        boss1.bossX_change *= 2.8
        if time_elapsed_since_last_action > 1000:
            boss1.bossX_change /= 2.8
            screen.blit(boss1.boss_laserImg, (x + 42, y + 256))
            boss_laser_var = mixer.Sound('laser-5.wav')
            boss_laser_var.set_volume(0.1)
            if boss_laser_sound == 0:
                boss_laser_var.play(0)
            boss_laser_sound += 1
            boss_colision(boss1, player1)
            if time_elapsed_since_last_action > 3000:
                boss_laser_sound = 0
                time_elapsed_since_last_action = 0
    if boss1.current_hp <= 0:
        win()

def fire_bullet(x, y, bullet1):
    global power_up
    bullet1.bullet_state = "fire"
    if power_up == 0:
        screen.blit(bullet1.bulletImg, (x + 16, y + 10))
    if power_up == 1:
        screen.blit(bullet1.bulletImg, (x + 8, y + 10))
        screen.blit(bullet1.bulletImg, (x + 24, y + 10))
    if power_up == 2 or power_up == 3:
        screen.blit(bullet1.bulletImg, (x, y + 10))
        screen.blit(bullet1.bulletImg, (x + 16, y + 10))
        screen.blit(bullet1.bulletImg, (x + 32, y + 10))
    if power_up >= 4:
        screen.blit(bullet1.bulletImg, (x - 16, y + 10))
        screen.blit(bullet1.bulletImg, (x, y + 10))
        screen.blit(bullet1.bulletImg, (x + 16, y + 10))
        screen.blit(bullet1.bulletImg, (x + 32, y + 10))
        screen.blit(bullet1.bulletImg, (x + 48, y + 10))

def star(x, y, star1):
    screen.blit(star1.starImg, (x + 16, y + 16))

player1 = Player()
bullet1 = Bullet()
star1 = Star()
boss1 = Boss()

def back_from_pause():
    global current_state, time_elapsed_since_last_action, time_elapsed_since_last_action2, xyz
    if current_state == 0:
        start_menu()
    if current_state == 1:
        main_game()
    if current_state == 2:
        stage2()

def start_menu():
    global over_game, score_value, high_score, current_state
    while True:
        screen.blit(background, (0, 0))
        over_text = font.render("PRESS SPACE TO PLAY", True, (255, 255, 255))
        screen.blit(over_text, (210, 250))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    over_game = False
                    current_state = 1
                    back_from_pause()
        pygame.display.update()

def pause():
    global over_game, score_value, high_score, current_state, time_elapsed_since_last_action,\
        from_pause, pause_laser, pause_laser_end, time_elapsed_since_last_action3, xyz
    while True:
        pause_laser += 1
        if pause_laser == 1:
            time_elapsed_since_last_action2 = copy.deepcopy(time_elapsed_since_last_action)
            xyz = time_elapsed_since_last_action2
            from_pause = True
            pause_laser_end = 0
        screen.blit(background, (0, 0))
        over_text = font.render("PRESS SPACE TO PLAY", True, (255, 255, 255))
        screen.blit(over_text, (210, 250))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause_laser = 0
                    back_from_pause()
        pygame.display.update()

def game_over():
    global paused, current_state, destroyed
    boss1.bossX = 800
    while True:
        dest = mixer.Sound('destroyed.wav')
        dest.set_volume(0.8)
        if destroyed == 0:
            dest.play(0)
            destroyed += 1
        screen.blit(background, (0, 0))
        game_over_text()
        over_text = font.render("PRESS SPACE TO PLAY", True, (255, 255, 255))
        screen.blit(over_text, (210, 250))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False
                    current_state = 1
                    destroyed = 0
                    back_from_pause()
        pygame.display.update()

def win():
    global over_game, score_value, current_state, power_up
    boss1.bossX = 800
    while True:
        screen.blit(background, (0, 0))
        power_up = 0
        text = font.render("CONGRATULATIONS, YOU WON!", True, (255, 255, 255))
        screen.blit(text, (150, 150))
        score_after = font.render("YOUR SCORE: " + str(score_value), True, (255, 255, 255))
        screen.blit(score_after, (250, 188))
        over_text = font.render("PRESS SPACE TO PLAY", True, (255, 255, 255))
        screen.blit(over_text, (210, 250))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    over_game = False
                    current_state = 1
                    score_value = 0
                    back_from_pause()
        pygame.display.update()


def stage2():
    global score_value, paused, current_state, time_elapsed_since_last_action, time_elapsed_since_last_action2, time_elapsed_since_last_action3
    while True:
        screen.blit(background, (0, 0))
        boss1.advanced_health()
        pygame.mouse.set_visible(False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    current_state = 2
                    time_elapsed_since_last_action3 = copy.deepcopy(time_elapsed_since_last_action)
                    pause()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player1.playerX_change = -5
            elif keys[pygame.K_RIGHT]:
                player1.playerX_change = 5
            else:
                player1.playerX_change = 0
            if keys[pygame.K_SPACE]:
                if bullet1.bullet_state == "ready":
                    bulletSound = mixer.Sound("laser.wav")
                    bulletSound.set_volume(0.1)
                    bulletSound.play()
                    bullet1.bulletX = player1.playerX
                    fire_bullet(bullet1.bulletX, bullet1.bulletY, bullet1)
        player1.playerX += player1.playerX_change
        boss1.bossX += boss1.bossX_change
        if player1.playerX <= 0:
            player1.playerX = 0
        elif player1.playerX >= 736:
            player1.playerX = 736
        if player1.playerX < (boss1.bossX + 98):
            boss1.bossX_change = -1.25
        elif player1.playerX > (boss1.bossX + 98):
            boss1.bossX_change = 1.25
        else:
            boss1.bossX_change = 0
        if bullet1.bulletY <= 0:
            bullet1.bulletY = 480
            bullet1.bullet_state = "ready"
        if bullet1.bullet_state == "fire":
            fire_bullet(bullet1.bulletX, bullet1.bulletY, bullet1)
            bullet1.bulletY -= bullet1.bulletY_change
        boss_distance = math.sqrt(math.pow((boss1.bossX + 100) - bullet1.bulletX, 2) + (
            math.pow((boss1.bossY + 100) - bullet1.bulletY, 2)))
        if boss_distance <= 120:
            explosionSound = mixer.Sound("explosion.wav")
            explosionSound.set_volume(0.05)
            explosionSound.play()
            bullet1.bulletY = 480
            bullet1.bullet_state = "ready"
            score_value += 1
            if power_up == 0:
                boss1.get_damage(1)
            if power_up == 1:
                boss1.get_damage(2)
            if power_up == 2:
                boss1.get_damage(3)
            if power_up in range(3, 5):
                boss1.get_damage(4)
            if power_up >= 5:
                boss1.get_damage(6)
        boss(boss1.bossX, boss1.bossY, boss1)
        boss_laser(boss1.bossX, boss1.bossY, boss1)
        player(player1.playerX, player1.playerY, player1)
        show_score(10, 10)
        clock.tick(180)
        pygame.display.update()

def main_game():
    global paused, background, score_value, enemyYcopy, enemyXcopy, enemyXchangecopy\
        ,time_elapsed_since_last_action, boom, over_game, high_score, star_cantbe, power_up, current_state, dt
    enemy1 = Enemy(paused)
    while True:
        dnt = clock.tick()
        if paused == True:
            enemy1.enemyX = enemyXcopy
            enemy1.enemyY = enemyYcopy
            enemy1.enemyX_change = enemyXchangecopy
            paused = False
        else:
            enemyXcopy = enemy1.enemyX.copy()
            enemyYcopy = enemy1.enemyY.copy()
            enemyXchangecopy = enemy1.enemyX_change.copy()
        pygame.mouse.set_visible(False)
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    current_state = 1
                    pause()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player1.playerX_change = -5
            elif keys[pygame.K_RIGHT]:
                player1.playerX_change = 5
            else:
                player1.playerX_change = 0
            if keys[pygame.K_SPACE]:
                if bullet1.bullet_state == "ready":
                    bulletSound = mixer.Sound("laser.wav")
                    bulletSound.set_volume(0.1)
                    bulletSound.play()
                    bullet1.bulletX = player1.playerX
                    fire_bullet(bullet1.bulletX, bullet1.bulletY, bullet1)
        player1.playerX += player1.playerX_change
        if player1.playerX <= 0:
            player1.playerX = 0
        elif player1.playerX >= 736:
            player1.playerX = 736
        if player1.playerY > 1000:
            player1.playerY = 480
        for i in range(enemy1.num_of_enemies):
            if enemy1.enemyY[i] > 410:
                high_score = copy.deepcopy(score_value)
                score_value = 0
                over_game = True
                star_cantbe = True
                game_over()
            enemy1.enemyX[i] += enemy1.enemyX_change[i]
            if enemy1.enemyX[i] <= 0:
                enemy1.enemyX_change[i] = 6
                enemy1.enemyY[i] += enemy1.enemyY_change[i]
            elif enemy1.enemyX[i] >= 736:
                enemy1.enemyX_change[i] = -6
                enemy1.enemyY[i] += enemy1.enemyY_change[i]
            distance = math.sqrt(math.pow(enemy1.enemyX[i] - bullet1.bulletX, 2) + (
                math.pow(enemy1.enemyY[i] - bullet1.bulletY, 2)))
            if distance < 30 and power_up == 0 or distance < 34 and power_up == 1 or distance < 38 and power_up == 2 \
                    or distance < 42 and power_up in range(3, 5) or distance < 50 and power_up >= 5:
                x = random.randint(1, 50)
                if x == 24:
                    star1.starX, star1.starY = enemy1.enemyX[i], enemy1.enemyY[i]
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.set_volume(0.1)
                explosionSound.play()
                screen.blit(boom, (enemy1.enemyX[i], enemy1.enemyY[i]))
                bullet1.bulletY = 480
                bullet1.bullet_state = "ready"
                score_value += 1
                enemy1.enemyX[i] = random.randint(0, 736)
                enemy1.enemyY[i] = random.randint(50, 150)
            star1.starY += star1.starY_change
            distance_star = math.sqrt(math.pow(star1.starX - player1.playerX, 2) + (
                math.pow(star1.starY - player1.playerY, 2)))
            if distance_star < 30 or star_cantbe == True:
                star1.starX = 2000
                star1.starY = 2000
                star_cantbe = False
                if distance_star < 30:
                    power_up += 1
            enemy(enemy1.enemyX[i], enemy1.enemyY[i], i, enemy1)
        if bullet1.bulletY <= 0:
            bullet1.bulletY = 480
            bullet1.bullet_state = "ready"
        if bullet1.bullet_state == "fire":
            fire_bullet(bullet1.bulletX, bullet1.bulletY, bullet1)
            bullet1.bulletY -= bullet1.bulletY_change
        if score_value >= 100:
            time_elapsed_since_last_action = 0
            boss1.current_hp = 200
            boss1.target_hp = 200
            stage2()
        star(star1.starX, star1.starY, star1)
        player(player1.playerX, player1.playerY, player1)
        show_score(10, 10)
        pygame.display.update()
        clock.tick(80)

if __name__ == "__main__":
    start_menu()
