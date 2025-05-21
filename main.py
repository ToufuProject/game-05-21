"""
今日やること
1 プレイヤーにライフをつける
1 敵にファイヤーボールを打たせる
2 ボスキャラを倒したらクリア演出

# memo.txtを見ながらやってみよう！

"""
import pygame
import os
import random
import math


"""
変数はまとめて書こう！！
"""
TATE = 900
YOKO = 1200
TITLE = "TAKOYAKI OISHI"

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "imgs")
PLAYER_DIR = os.path.join(IMG_DIR, "resized_ningen2025.png")
BOSS_DIR = os.path.join(IMG_DIR, "mabuta.png")
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
BGM_PATH = os.path.join(SOUND_DIR, "bgm.mp3")

all_sprites = pygame.sprite.Group()
teki_hako = pygame.sprite.Group()
fireballs = pygame.sprite.Group()
boss_fireballs= pygame.sprite.Group()

clear = False
game_over = False
last_enemy_time = 0
kurikaeshi = True
music_done = False


pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(BGM_PATH)
screen = pygame.display.set_mode((YOKO, TATE))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        gazou = pygame.image.load(PLAYER_DIR).convert()
        self.image.blit(gazou, (0, 0), (0, 0, 32, 32))
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect   = self.image.get_rect(x=600, y=100)
        self.vx = 0
        self.vy = 0
        self.uteru = True

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] == True:
            self.vx = 1
        elif keys[pygame.K_LEFT] == True:
            self.vx = -1
        elif keys[pygame.K_UP] == True:
            self.vy = -1
        elif keys[pygame.K_DOWN] == True:
            self.vy = 1
        else:
            self.vx = 0
            self.vy = 0
        self.rect.x += self.vx
        self.rect.y += self.vy
        # もしもスペースを押したらファイヤーボールを出す
        # ファイヤーボールを初期化して、それをall_spritesにしまう
        if keys[pygame.K_SPACE]:
            if self.uteru:
                fireball = Fireball(x=self.rect.x, y=self.rect.y)
                fireballs.add(fireball)
                all_sprites.add(fireball)
                self.uteru = False
        else:
            self.uteru = True


class Teki(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        gazou = pygame.image.load(PLAYER_DIR).convert()
        self.image.blit(gazou, (0, 0), (0, 0, 32, 32))
        self.rect = self.image.get_rect(x=10, y=random.randint(0, 30))
        self.vx = 1

    def update(self):
        self.rect.x += self.vx

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 0, 0))
        self.rect  = self.image.get_rect(center=(x, y))
        self.vx = -1

    def update(self):
        self.rect.x += self.vx
        if self.rect.right < 0:
            self.kill()


class BossFireball(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_deg, speed, color):
        super().__init__()
        self.image = pygame.Surface((10,10)); self.image.fill(color)
        self.posx, self.posy = float(x), float(y)
        rad  = math.radians(angle_deg)
        self.vx = speed * math.cos(rad); self.vy = speed * math.sin(rad)
        self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.posx += self.vx; self.posy += self.vy
        self.rect.center = (int(self.posx), int(self.posy))
        if (self.rect.right < 0 or self.rect.left > YOKO or
            self.rect.bottom < 0 or self.rect.top > TATE): self.kill()



class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.rect  = self.image.get_rect(center=(100, 450))   # ← 左端に配置
        self.max_life = 50
        self.life  = self.max_life
        self.bullet_speed = 1       # ← 全弾共通スピード

        self.patterns = [
            {"dur":5,"bcol":(255,32,32),"fcol":(0,128,255),"func":self.p_radial},
            {"dur":4,"bcol":(32,255,32),"fcol":(255,215,0),"func":self.p_fiveway},
            {"dur":6,"bcol":(200,32,255),"fcol":(255,64,255),"func":self.p_sine}
        ]
        self.idx   = 0
        self.start = pygame.time.get_ticks()/1000
        self.spin  = 0

    # 0. 回転花火
    def p_radial(self, now, col):
        if not hasattr(self, "nt0"): self.nt0 = 0
        if now >= self.nt0:
            for ang in range(0, 360, 20):
                bf = BossFireball(self.rect.centerx, self.rect.centery,
                                  ang + self.spin, self.bullet_speed, col)
                boss_fireballs.add(bf); all_sprites.add(bf)
            self.spin = (self.spin + 12) % 360
            self.nt0  = now + 1.0

    # 1. 5way 狙撃
    def p_fiveway(self, now, col):
        if not hasattr(self, "nt1"): self.nt1 = 0
        if now >= self.nt1:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            base = math.degrees(math.atan2(dy, dx))
            for off in (-15, -7, 0, 7, 15):
                bf = BossFireball(self.rect.centerx, self.rect.centery,
                                  base + off, self.bullet_speed + 1, col)
                boss_fireballs.add(bf); all_sprites.add(bf)
            self.nt1 = now + 0.8

    # 2. サインストリーム（← 角度を 0° に修正）
    def p_sine(self, now, col):
        if int(now * 10) % 3 == 0:                # 0.3 秒ごと
            bf = BossFireball(self.rect.centerx, self.rect.centery,
                              0,                 # → 右向き
                              self.bullet_speed, col)
            bf.sy = bf.posy
            bf.ph = now
            bf.update = lambda b=bf: sine_update(b)
            boss_fireballs.add(bf); all_sprites.add(bf)

    # 共通 update
    def update(self):
        now = pygame.time.get_ticks() / 1000
        pat = self.patterns[self.idx]
        self.image.fill(pat["bcol"])
        pat["func"](now, pat["fcol"])
        if now - self.start > pat["dur"]:
            self.idx   = (self.idx + 1) % len(self.patterns)
            self.start = now
            for attr in ("nt0", "nt1"):
                if hasattr(self, attr):
                    delattr(self, attr)

"""
追加
"""
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(random.choice([
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]))
        self.rect = self.image.get_rect(
            center=(random.randint(0, YOKO), random.randint(-100, 0))
        )
        self.speed = random.uniform(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > TATE:
            self.kill()




def draw_boss_life(screen, boss):
    BAR_W, BAR_H = boss.rect.width, 6
    x, y = boss.rect.left, boss.rect.bottom + 10
    pygame.draw.rect(screen, (80, 80, 80), (x, y, BAR_W, BAR_H))

    ratio = max(0, boss.life / boss.max_life)
    hp_w  = int(BAR_W * ratio)

    if ratio >= .5:
        t = (ratio - .5) * 2
        col = (int(255 * (1 - t)), 255, 0)
    else:
        t = ratio * 2
        col = (255, int(255 * t), 0)
    pygame.draw.rect(screen, col, (x, y, hp_w, BAR_H))

def sine_update(b):
    b.posx+=b.vx
    b.posy=b.sy+50*math.sin(b.posx/60+b.ph)
    b.rect.center=(int(b.posx),int(b.posy))
    if (b.rect.right<0 or b.rect.left>YOKO or
        b.rect.bottom<0 or b.rect.top>TATE): b.kill()

player = Player()
all_sprites.add(player)
boss = Boss()
all_sprites.add(boss)

while kurikaeshi:
    current_time = pygame.time.get_ticks() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            kurikaeshi = False

    if not game_over:
        if current_time - last_enemy_time > 1.5:
            teki = Teki()
            teki_hako.add(teki)
            last_enemy_time = current_time

        if pygame.sprite.spritecollide(player, teki_hako, dokill=True):
            game_over = True
        if pygame.sprite.spritecollide(player, boss_fireballs, dokill=True):
            game_over = True

        if boss.alive():
            hits = pygame.sprite.spritecollide(boss, fireballs, dokill=True)
            if hits:
                boss.life -= len(hits)
                if boss.life <= 0:
                    boss.kill()

        all_sprites.update()
        teki_hako.update()
    """
    追加
    """
    if clear:
        if not music_done:
            print("ゲームくりあ")

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    teki_hako.draw(screen)

    # ボスのライフバー
    if boss.alive():
        draw_boss_life(screen, boss)
        #print("生きてるよ〜ん")

    # クリアメッセージ
    if clear:
        f_big = pygame.font.SysFont(None, 74)
        txt_big = f_big.render('GAME CLEAR!!', True, (255, 255, 0))
        rect_big = txt_big.get_rect(center=(YOKO/2, TATE/2))
        screen.blit(txt_big, rect_big)

    # ゲームオーバーメッセージ
    if game_over:
        f_big = pygame.font.SysFont(None, 74)
        f_small = pygame.font.SysFont(None, 24)

        txt_big = f_big.render('IKEMEN TAKAHASHI', True, (255, 255, 255))
        rect_big = txt_big.get_rect(center=(YOKO/2, TATE/2))
        screen.blit(txt_big, rect_big)

        txt_small = f_small.render('Press Space to Restart', True, (255, 255, 255))
        rect_small = txt_small.get_rect(center=(YOKO/2, TATE/2 + 70))
        screen.blit(txt_small, rect_small)

    pygame.display.flip()


pygame.quit()