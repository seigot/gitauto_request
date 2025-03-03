import pygame
import random
import sys

pygame.init()

# 画面サイズ・ゲーム設定
WIDTH, HEIGHT = 800, 600
FPS = 60
BRICK_ROWS = 5
BRICK_COLUMNS = 10
BRICK_WIDTH = 70
BRICK_HEIGHT = 20
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 10

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
RED     = (255, 0,   0)
BLUE    = (0,   0,   255)
YELLOW  = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ドラゴンクエストみたいなゲーム")
clock = pygame.time.Clock()

# パドル
paddle = pygame.Rect((WIDTH - PADDLE_WIDTH)//2, HEIGHT-40, PADDLE_WIDTH, PADDLE_HEIGHT)

# ボール
ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_RADIUS*2, BALL_RADIUS*2)
ball_vel = [4, -4]

# ブロック配置
brick_padding = 5
offset_top = 50
offset_left = (WIDTH - (BRICK_COLUMNS * (BRICK_WIDTH + brick_padding))) // 2

def create_bricks():
    bricks_local = []
    for row in range(BRICK_ROWS):
        row_list = []
        for col in range(BRICK_COLUMNS):
            x = offset_left + col*(BRICK_WIDTH+brick_padding)
            y = offset_top  + row*(BRICK_HEIGHT+brick_padding)
            row_list.append(pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT))
        bricks_local.append(row_list)
    return bricks_local

bricks = create_bricks()

# スコア
score = 0
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

# パーティクル管理
particles = []
def create_particles(x, y):
    for _ in range(20):
        particles.append([
            x,                   # x座標
            y,                   # y座標
            random.randint(-3,3),# x方向速度
            random.randint(-3,3),# y方向速度
            random.randint(20,40)# 寿命
        ])

def update_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1
        if p[4] <= 0:
            particles.remove(p)

def draw_particles(screen):
    for p in particles:
        px, py, vx, vy, life = p
        pygame.draw.circle(screen, YELLOW, (int(px), int(py)), 3)

# 壊れたブロックのフェードアウト演出
broken_bricks = []
def create_broken_brick_effect(brick):
    # [center_x, center_y, w, h, alpha]
    broken_bricks.append([brick.centerx, brick.centery, brick.width, brick.height, 255])

def update_broken_bricks():
    fade_speed = 10
    for b in broken_bricks[:]:
        b[4] -= fade_speed
        if b[4] <= 0:
            broken_bricks.remove(b)

def draw_broken_bricks(screen):
    for b in broken_bricks:
        cx, cy, w, h, alpha = b
        rx = cx - w//2
        ry = cy - h//2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((255, 0, 0, alpha))  # RGBA
        screen.blit(surf, (rx, ry))

def reset_bricks():
    global bricks
    bricks = create_bricks()

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -----------------------------------------
    # パドルをボールの真下に合わせる（自動操作）
    # -----------------------------------------
    paddle.x = ball.centerx - PADDLE_WIDTH//2
    # 画面端をはみ出さないように補正
    if paddle.x < 0:
        paddle.x = 0
    if paddle.x + PADDLE_WIDTH > WIDTH:
        paddle.x = WIDTH - PADDLE_WIDTH

    # -----------------------------------------
    # ボールの移動
    # -----------------------------------------
    ball.x += ball_vel[0]
    ball.y += ball_vel[1]

    # 壁との衝突判定 (左右)
    if ball.left < 0:
        ball.left = 0
        ball_vel[0] = -ball_vel[0]
    elif ball.right > WIDTH:
        ball.right = WIDTH
        ball_vel[0] = -ball_vel[0]

    # 壁との衝突判定 (上)
    if ball.top < 0:
        ball.top = 0
        ball_vel[1] = -ball_vel[1]

    # 画面下まで落ちたら終了
    if ball.bottom > HEIGHT:
        running = False

    # 壁衝突後に横速度が 0 に近ければ微調整（真上・真下防止）
    if abs(ball_vel[0]) < 0.1:
        ball_vel[0] = random.choice([-1, 1])

    # -----------------------------------------
    # パドルとの衝突：衝突位置で角度を変える
    # -----------------------------------------
    if ball.colliderect(paddle) and ball_vel[1] > 0:
        # パドル中心を基準に (-1.0 ~ +1.0)
        relative_x = (ball.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
        max_speed = 6
        ball_vel[0] = relative_x * max_speed
        ball_vel[1] = -abs(ball_vel[1])  # 上向きに反転

        # 衝突後、横速度が小さ過ぎる場合はランダムにずらす
        if abs(ball_vel[0]) < 0.3:
            ball_vel[0] = random.choice([-1.5, 1.5])

    # -----------------------------------------
    # ブロックとの衝突
    # -----------------------------------------
    hit_brick = False
    for row in bricks:
        for brick in row:
            if ball.colliderect(brick):
                # どの方向から衝突したか
                dx = ball.centerx - brick.centerx
                dy = ball.centery - brick.centery
                if abs(dx) > abs(dy):
                    ball_vel[0] = -ball_vel[0]
                else:
                    ball_vel[1] = -ball_vel[1]

                # パーティクル＆演出
                create_particles(brick.centerx, brick.centery)
                create_broken_brick_effect(brick)
                row.remove(brick)
                score += 100
                hit_brick = True
                break
        if hit_brick:
            break

    # 衝突後にまた速度チェック（真上/真横防止）
    if abs(ball_vel[0]) < 0.1:
        ball_vel[0] = random.choice([-1, 1])

    # 全ブロック破壊したら再配置
    if all(len(row) == 0 for row in bricks):
        score += 1000
        reset_bricks()

    # パーティクル・壊れブロック演出更新
    update_particles()
    update_broken_bricks()

    # -----------------------------------------
    # 描画
    # -----------------------------------------
    screen.fill(BLACK)

    # パドルとボール
    pygame.draw.rect(screen, BLUE, paddle)
    pygame.draw.ellipse(screen, YELLOW, ball)

    # ブロック
    for row in bricks:
        for brick in row:
            pygame.draw.rect(screen, RED, brick)

    # パーティクル＆壊れブロック
    draw_particles(screen)
    draw_broken_bricks(screen)

    # スコア表示
    score_text = font.render('Score: ' + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
