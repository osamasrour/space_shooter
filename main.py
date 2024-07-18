# ====== import some modules =======
import pygame
from os.path import join, dirname
from os import chdir
from sys import exit
from random import randint, choice
from configparser import ConfigParser
from termcolor import colored
from functools import wraps
from project.classes.button import Button
from project.classes.player import Player
from project.classes.bullet import Bullet
from project.classes.enemy import Enemy

# ====== set up the game env =======
pygame.init()
chdir(dirname(__file__))
# try to make connection to the configeration file to setup the game
try:
    config = ConfigParser()
    # if the sections is empty then the file isn't in the directory we in
    assert config.read("settings.cfg") != []
except AssertionError:
    print(f"cannot connect to the \"{colored(" settings.cfg ", "light_red")}\" file")
    exit()

# ====== set up some variables =====
WIDTH, HEIGHT = config.getint("Default", "WIDTH"), config.getint("Default", "HEIGHT")
FPS = config.getint("Default", "fps")
GameStatus = config.get("Default", "GameStatus") # or "game play" or "pouse menu" or "game over"
level = config.getint("Default", "level")
score = config.getint("Default", "score")
lives = config.getint("Default", "lives")
clock = pygame.time.Clock()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# ====== loading the assets =========
# images
ICON = pygame.image.load(join("assets", "images", "ufo.png")).convert_alpha()
BG = pygame.transform.scale(pygame.image.load(
    join("assets", "images", "background.png")).convert_alpha(), (WIDTH, HEIGHT))
playerimg = pygame.image.load(join("assets", "images", "player.png")).convert_alpha()
barimg = pygame.transform.scale(playerimg, (30, 30)).convert_alpha()
enemyimg = pygame.image.load(join("assets", "images", "enemy.png")).convert_alpha()
bulletimg = pygame.image.load(join("assets", "images", "bullet.png")).convert_alpha()
ebulletimg = pygame.image.load(join("assets", "images", "ebullet.png")).convert_alpha()
# sounds
explosion_sound = pygame.mixer.Sound(join("assets", "sounds", "explosion.wav"))
laser_sound = pygame.mixer.Sound(join("assets", "sounds", "laser.wav"))
background_sound = pygame.mixer.music.load(join("assets", "sounds", "background.wav"))

# ====== set the caption and the icon ======
pygame.display.set_caption(config.get("Default", "WinName"))
pygame.display.set_icon(ICON)

# ======= game labales ============
# define the font
MainFont = pygame.font.SysFont("comic sans", 35)
GameOverFont = pygame.font.SysFont("freesansblod", 150)
PressENTERfont = pygame.font.SysFont("Arial", 20)
# define the functions
# score func
def ShowScore():
    global score_labale
    score_labale = MainFont.render(f"Score : {score}", True, (255, 255, 255))
    WIN.blit(score_labale, (5, 5))

# levels func
def ShowLevel():
    global level_labale
    level_labale = MainFont.render(f"Level : {level}", True, (255, 255, 255))
    WIN.blit(level_labale, (WIDTH - level_labale.get_width() - 5, 5))

# lives bar
def LivesBar():
    WIN.blit(barimg, (5, level_labale.get_height() + 5))
    pygame.draw.rect(WIN, (255, 0, 0), (barimg.get_width() + 10, 
                                        level_labale.get_height() + 15, 110, 10))
    pygame.draw.rect(WIN, (0, 255, 0), (barimg.get_width() + 10, 
                                        level_labale.get_height() + 15, 110 / 
                                        config.getint("Default", "lives") * lives, 10))

# game over screen
GameOverText = GameOverFont.render("GAME OVER", True, (255, 0, 0))
PressENTER = PressENTERfont.render("Please press \"ENTER\" to start again", True, (255, 225, 0))
def GameOver():
    global enemys_num, score, GameStatus, level, enemys, game_over_counter, lives, enemysbullets
    if game_over_counter <= FPS * 4:
        game_over_counter += 1
        WIN.blit(BG, (0, 0))
        WIN.blit(PressENTER, (WIDTH // 2 - PressENTER.get_width() // 2,
                                HEIGHT // 2 - GameOverText.get_height() // 2 - 
                                PressENTER.get_height() - 10))
        WIN.blit(GameOverText, (WIDTH // 2 - GameOverText.get_width() // 2,
                                HEIGHT // 2 - GameOverText.get_height() // 2))
        WIN.blit(score_labale, (WIDTH // 2 - score_labale.get_width() // 2,
                                HEIGHT // 2 - score_labale.get_height() // 2 + 
                                GameOverText.get_height() // 2 + 10))
        WIN.blit(level_labale, (WIDTH // 2 - level_labale.get_width() // 2,
                                HEIGHT // 2 - level_labale.get_height() // 2 + 
                                GameOverText.get_height() // 2 + 20 + 
                                score_labale.get_height() // 2))
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            score = config.getint("Default", "score")
            level = config.getint("Default", "level")
            lives = config.getint("Default", "lives")
            GameStatus = "game play"
            enemys_num = config.getint("Default", "EnemysNum")
            enemys = []
            enemysbullets = []
            for _ in range(enemys_num):
                enemy = Enemy(enemyimg, randint(10, WIDTH - enemyimg.get_width() - 20), 
                            randint(50,150), choice([-5, 5]), 1)
                enemys.append(enemy)
    else:
        GameStatus = "start menu"
        score = config.getint("Default", "score")
        level = config.getint("Default", "level")
        lives = config.getint("Default", "lives")
        enemys_num = config.getint("Default", "EnemysNum")
        enemys = []
        for _ in range(enemys_num):
            enemy = Enemy(enemyimg, randint(10, WIDTH - enemyimg.get_width() - 20), 
                        randint(50,150), choice([-5, 5]), 1)
            enemys.append(enemy)

# ======== collide function ========
def collide(obj1, obj2, m = 0):
    offset_x = obj1.x - obj2.x + m # problem in the images
    offset_y = obj1.y - obj2.y + m # problem in the images
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y))

# ======= inistantiate objects =======
# buttons
start_btn = Button("Start", (WIDTH // 2 - 73, 150), 55)
exit_btn = Button("Exit", (WIDTH // 2 - 60, 300), 55)
audio_btn = Button("Audio", (20, HEIGHT // 4 * 1), 55)
back_btn = Button("Back", (20, HEIGHT // 4 * 3), 55)
options_btn = Button("Options", (WIDTH // 2 - 115, HEIGHT // 6 * 3), 55)
quit_btn = Button("Quit", (WIDTH // 2 - 65, HEIGHT // 6 * 4), 55)
start_over_btn = Button("Start", (WIDTH // 2 - 80, HEIGHT // 6 * 2), 55)
resume_btn = Button("Resume", (WIDTH // 2 - 118, HEIGHT // 6 * 1), 55)
video_btn = Button("Video", (20, HEIGHT // 4 * 2), 55)
audio_X_video_back_btn = Button("Back", (606, 493), 55)
laser_arrow_right_btn = Button(">", (690, 100), 30, TextColor="red")
laser_arrow_left_btn = Button("<", (561, 100), 30, TextColor="blue")
explosion_arrow_right_btn = Button(">", (670, 250), 30, TextColor="red")
explosion_arrow_left_btn = Button("<", (535, 250), 30, TextColor="blue")
background_arrow_right_btn = Button(">", (690, 400), 30, TextColor="red")
background_arrow_left_btn = Button("<", (553, 400), 30, TextColor="blue")
FPS_arrow_right_btn = Button(">", (690, 100), 30, TextColor="red")
FPS_arrow_left_btn = Button("<", (561, 100), 30, TextColor="blue")
numEnemy_arrow_right_btn = Button(">", (719, 400), 30, TextColor="red")
numEnemy_arrow_left_btn = Button("<", (490, 400), 30, TextColor="blue")
pouse_btn = Button("█ █", (720, 50), 20, TextColor="black", bgcolor1="olive", bgcolor2="olive")

# Pouse Button => q
Q_Pouse_font = pygame.font.SysFont("Pixeltype", 30)
Q_Pouse_text = Q_Pouse_font.render("Q", True, (0, 0, 255))
def Q_Pouse():
    pouse_btn.draw(WIN)
    pygame.draw.rect(WIN, (0, 0, 0), (757, 87, 23, 23), border_radius= 20)
    WIN.blit(Q_Pouse_text, (760, 90))

# player
player = Player(playerimg, WIDTH // 2 - playerimg.get_width() // 2, 
                HEIGHT - playerimg.get_height() - 10, 1)
player_bullets = []
shoot = False
shoot_counter = 0

# enemy
enemys_num = config.getint("Default", "EnemysNum")
enemys = []
enemysbullets = []
for i in range(enemys_num):
    enemy = Enemy(enemyimg, randint(10, WIDTH - enemyimg.get_width() - 20), 
                randint(50,150), choice([-5, 5]), 1)
    enemys.append(enemy)

# ====== close function ===========
def Close():
    global run
    run = False
    pygame.quit()
    exit()

# ======= the start menu function =======
def StartMenu():
    global GameStatus
    WIN.fill((0, 50, 90))
    start_btn.draw(WIN)
    if start_btn.isclicked():
        GameStatus = "game play"
    exit_btn.draw(WIN)
    if exit_btn.isclicked():
        Close()

# ======== the game play function ========
def GamePlay():
    global enemys_num, score, GameStatus, level, enemys
    global game_over_counter, lives, shoot, shoot_counter
    WIN.blit(BG, (0, 0))
    ShowScore()
    ShowLevel()
    LivesBar()
    Q_Pouse()
    # set the sound's volume
    explosion_sound.set_volume(config.getfloat("Default", "explosionvolume"))
    laser_sound.set_volume(config.getfloat("Default", "laservolume"))
    player.draw(WIN, 10)
    # frames between shoots counter
    if shoot_counter > 0:
        shoot_counter -= 1
    if pygame.key.get_pressed()[pygame.K_q]:
        GameStatus = "pouse menu"
    for i in range(enemys_num -1, -1, -1):
        enemys[i].draw(WIN)
        if enemys[i].y >= 400:
            GameStatus = "game over"
            game_over_counter = 0
        if randint(0, FPS * 3) == 1:
            eb = Bullet(ebulletimg, enemys[i], 1)
            enemysbullets.append(eb)
    if pygame.key.get_pressed()[pygame.K_SPACE] == True and shoot == False and shoot_counter == 0:
        # rest the frames counter
        shoot_counter = 0.5 * FPS
        # make a new bullet object
        pb = Bullet(bulletimg, player, 1)
        # add the bullet to the bullets list
        player_bullets.append(pb)
        # make a shoot sound
        laser_sound.play()
        shoot = True
    if pygame.key.get_pressed()[pygame.K_SPACE] == False:
        shoot = False
    # loop on player_bullets list
    for i in range(len(player_bullets) - 1, -1, -1):
        # catch the collision between any enemy and the bullet
        for j in range(enemys_num - 1, -1, -1):
            if collide(enemys[j], player_bullets[i], m=20):
                score += 1
                enemys_num -= 1
                del enemys[j]
                player_bullets[i].dead = True 
                explosion_sound.play()
        # blit the player's bullets on the screen if no collision happend or goes off the screen
        if player_bullets[i].dead == True:
            del player_bullets[i]
        else:
            player_bullets[i].draw(WIN, -10)
    # blit the enemys' bullets if no collision happend or goes off the screen
    for i in range(len(enemysbullets) - 1, -1, -1):
        if enemysbullets[i].dead == True:
            del enemysbullets[i]
        else:
            enemysbullets[i].draw(WIN, 7)
            # catch collition between player and bullets
            if collide(player, enemysbullets[i], m=-40):
                enemysbullets[i].dead = True
                lives -= 1
    # lose handler
    if lives <= 0:
        GameStatus = "game over"
        game_over_counter = 0
    # refull the "enemys'" list
    if enemys_num == 0:
        enemys_num = config.getint("Default", "enemysnum")
        level += 1
        for i in range(enemys_num):
            enemy = Enemy(enemyimg, randint(10, WIDTH - enemyimg.get_width() - 20), 
                        randint(50,150), choice([-5, 5]), 1)
            enemys.append(enemy)

# ====== the pouse menu function =======
def PouseMenu():
    global GameStatus, score, level, lives, enemys, enemysbullets, player_bullets, enemys_num, modified
    WIN.fill((0, 50, 90))
    resume_btn.draw(WIN)
    if resume_btn.isclicked() and modified == False:
        GameStatus = "game play"
    start_over_btn.draw(WIN)
    if start_over_btn.isclicked():
        modified = False
        score = config.getint("Default", "score")
        level = config.getint("Default", "level")
        lives = config.getint("Default", "lives")
        enemys_num = config.getint("Default", "enemysnum")
        enemys = []
        enemysbullets = []
        player_bullets = []
        for _ in range(enemys_num - 1, -1, -1):
            enemy = Enemy(enemyimg, randint(10, WIDTH - enemyimg.get_width() - 20), 
                        randint(50,150), choice([-5, 5]), 1)
            enemys.append(enemy)
        GameStatus = "game play"
    options_btn.draw(WIN)
    if options_btn.isclicked():
        GameStatus = "options menu"
    quit_btn.draw(WIN)
    if quit_btn.isclicked():
        Close()

# ======= options menu =========
def OptionsMenu():
    global GameStatus
    WIN.fill((0, 50, 90))
    audio_btn.draw(WIN)
    if audio_btn.isclicked():
        GameStatus = "audio menu"
    video_btn.draw(WIN)
    if video_btn.isclicked():
        GameStatus = "video menu"
    back_btn.draw(WIN)
    if back_btn.isclicked():
        GameStatus = "pouse menu"

# ====== settings handler ======
# decorator we ganna need
def configdec(func):
    config.read("settings.cfg")
    @wraps(func)
    def wrapper(*arg, **kwargs):
        func(*arg, **kwargs)
        with open("settings.cfg",  "w") as f:
            config.write(f)
            f.close()
    return wrapper

# laser volume handler
@configdec
def LaserVolumeHandler(value: float):
    config.set("Default", "laservolume",
                str(round(config.getfloat("Default", "laservolume") + value, 1)))

# explosion volume handler
@configdec
def ExplosionVolumeHandler(value: float):
    config.set("Default", "explosionvolume",
                str(round(config.getfloat("Default", "explosionvolume") + value, 3)))

# background volume handler
@configdec
def BackGroundVolumeHandler(value: float):
    config.set("Default", "backgroundvolume",
                str(round(config.getfloat("Default", "backgroundvolume") + value, 2)))

# fps handler
@configdec
def FPSHandler(value: int):
    config.set("Default", "fps", str(value))

# difficulty levels handler
@configdec
def DifficultyHandler(value: int):
    config.set("Default", "enemysnum", str(value))

# audio and video lables
AudioXVideoMenuFont = pygame.font.SysFont("Arial", 50)
LaserVolumeText = AudioXVideoMenuFont.render("Laser Volume", True, (51, 251, 51))
ExplosionVolumeText = AudioXVideoMenuFont.render("Explosion Volume", True, (51, 251, 51))
BackGroundVolumeText = AudioXVideoMenuFont.render("Back Ground Volume", True, (51, 251, 51))
FremesPeerSecText = AudioXVideoMenuFont.render("FPS", True, (51, 251, 51))
NumberOfTheEnemysText = AudioXVideoMenuFont.render("Number Of The Enemys", True, (51, 251, 51))

# ========== Audio menu ========
def AudioMenu():
    global GameStatus
    WIN.fill((0, 50, 90))
    # laser volume bliter
    WIN.blit(LaserVolumeText, (20, 100))
    laser_arrow_left_btn.draw(WIN)
    if laser_arrow_left_btn.isclicked() and config.getfloat("Default", "laservolume") > 0:
        LaserVolumeHandler(-0.1)
    LaserVolumeValue = AudioXVideoMenuFont.render(f"{int(100 * round(config.getfloat("Default", "laservolume"),
                                                            1))}", True, (0, 255, 255))
    WIN.blit(LaserVolumeValue, (laser_arrow_left_btn.x + laser_arrow_left_btn.width + 5, 100))
    laser_arrow_right_btn.draw(WIN)
    if laser_arrow_right_btn.isclicked() and config.getfloat("Default", "laservolume") < 1:
        LaserVolumeHandler(0.1)
    # explosion volume bliter
    WIN.blit(ExplosionVolumeText, (20, 250))
    explosion_arrow_left_btn.draw(WIN)
    if explosion_arrow_left_btn.isclicked() and config.getfloat("Default", "explosionvolume") > 0:
        ExplosionVolumeHandler(-0.005)
    ExplosionVolumeValue = AudioXVideoMenuFont.render(f"{int(round(
        config.getfloat("Default", "explosionvolume"), 3) / 0.1 * 100)}", True, (0, 255, 255))
    WIN.blit(ExplosionVolumeValue, (explosion_arrow_left_btn.x + 
                                    explosion_arrow_left_btn.width + 5, 250))
    explosion_arrow_right_btn.draw(WIN)
    if explosion_arrow_right_btn.isclicked() and config.getfloat("Default", "explosionvolume") < 0.1:
        ExplosionVolumeHandler(0.005)
    # back ground volume bliter
    WIN.blit(BackGroundVolumeText, (20, 400))
    background_arrow_left_btn.draw(WIN)
    if background_arrow_left_btn.isclicked() and config.getfloat("Default", "backgroundvolume") > 0:
        BackGroundVolumeHandler(-0.01)
    BackGroundVolumeValue = AudioXVideoMenuFont.render(
        f"{int(round(config.getfloat("Default", "backgroundvolume"), 2) / 0.15 * 100)}", True, (0, 255, 255))
    WIN.blit(BackGroundVolumeValue, (background_arrow_left_btn.x + 
                                    background_arrow_left_btn.width + 5, 400))
    background_arrow_right_btn.draw(WIN)
    if background_arrow_right_btn.isclicked() and config.getfloat("Default", "backgroundvolume") < 0.15:
        BackGroundVolumeHandler(0.01)
    # back button => to go back to the "options menu"
    audio_X_video_back_btn.draw(WIN)
    if audio_X_video_back_btn.isclicked():
        GameStatus = "options menu"

# ======= video menu ========
frames_list = [10, 20, 30, 60, 90, 120]
listpointer = frames_list.index(config.getint("Default", "fps"))
difficulty_levels = {
    "Easy": 7,
    "Medium": 10,
    "Hard": 15
}
dictpointer = list(difficulty_levels.values()).index(config.getint("Default", "enemysnum"))
modified = False

def VideoMenu():
    global GameStatus, listpointer, FPS, dictpointer, modified
    WIN.fill((0, 50, 90))
    # frames bliter
    WIN.blit(FremesPeerSecText, (20, 100))
    FPS_arrow_left_btn.draw(WIN)
    if FPS_arrow_left_btn.isclicked() and listpointer > 0:
        modified = True
        listpointer -= 1
        FPSHandler(frames_list[listpointer])
    FPSvalue = AudioXVideoMenuFont.render(f"{config.getint("Default", "fps")}", True, (0, 255, 255))
    WIN.blit(FPSvalue, (FPS_arrow_left_btn.x + FPS_arrow_left_btn.width + 5, 100))
    FPS_arrow_right_btn.draw(WIN)
    if FPS_arrow_right_btn.isclicked() and listpointer < len(frames_list) - 1:
        modified = True
        listpointer += 1
        FPSHandler(frames_list[listpointer])
    FPS = config.getint("Default", "fps")
    # enemy number bliter
    WIN.blit(NumberOfTheEnemysText, (20, 320))
    numEnemy_arrow_left_btn.draw(WIN)
    if numEnemy_arrow_left_btn.isclicked() and dictpointer > 0:
        modified = True
        dictpointer -= 1
        DifficultyHandler(difficulty_levels[list(difficulty_levels.keys())[dictpointer]])
    NumEnemydifficulty = AudioXVideoMenuFont.render(
        f"{list(difficulty_levels.keys())[dictpointer]}", True, (0, 255, 255))
    WIN.blit(NumEnemydifficulty, (numEnemy_arrow_left_btn.x + numEnemy_arrow_left_btn.width + 5, 400))
    numEnemy_arrow_right_btn.draw(WIN)
    if numEnemy_arrow_right_btn.isclicked() and dictpointer < len(list(difficulty_levels.keys())) - 1:
        modified = True
        dictpointer += 1
        DifficultyHandler(difficulty_levels[list(difficulty_levels.keys())[dictpointer]])
    # back button => to go back to the "options menu"
    audio_X_video_back_btn.draw(WIN)
    if audio_X_video_back_btn.isclicked():
        GameStatus = "options menu"

# the App (main function)
def App():
    pygame.mixer.music.set_volume(config.getfloat("Default", "BackgroundVolume")) # set the Background music volume
    pygame.mixer.music.play(-1) # playing the music in the background continuesly
    run = True
    while run:
        clock.tick(FPS) # set the FPS for the Game Loop
        pygame.mixer.music.set_volume(config.getfloat("Default", "BackgroundVolume")) # set the Background music volume
        # status handler
        if GameStatus == "start menu":
            StartMenu()
        if GameStatus == "game play":
            GamePlay()
        if GameStatus == "pouse menu":
            PouseMenu()
        if GameStatus == "game over":
            GameOver()
        if GameStatus == "options menu":
            OptionsMenu()
        if GameStatus == "audio menu":
            AudioMenu()
        if GameStatus == "video menu":
            VideoMenu()
        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Close()
        # update the Window
        pygame.display.update()

if __name__ == "__main__":
    #  Run the app
    App()
    # delete the modulse from the memory after closing the Game
    del (pygame, Button, Bullet, Player, Enemy, chdir, exit, 
        dirname ,choice, randint,ConfigParser, colored, wraps)
